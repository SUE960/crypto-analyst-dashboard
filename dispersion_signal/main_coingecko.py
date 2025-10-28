#!/usr/bin/env python3
"""
Dispersion Signal - CoinGecko 데이터 수집기 (무료 버전)
메인 실행 스크립트
"""
import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID

# 프로젝트 모듈 임포트
from config import Config
from collectors.coingecko import CoinGeckoCollector
from database.supabase_client import SupabaseClient
from database.models_coingecko import MarketMetric, PriceHistory, ExchangeData
from utils.logger import setup_logger, log_data_collection, log_error

def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='CoinGecko 암호화폐 데이터 수집기 (무료)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main_coingecko.py --symbol BTC --days 7
  python main_coingecko.py --symbol ETH --days 3
  python main_coingecko.py --list-symbols
  python main_coingecko.py --test-connection
        """
    )
    
    parser.add_argument(
        '--symbol', 
        type=str, 
        default='BTC',
        help='수집할 코인 심볼 (기본값: BTC)'
    )
    
    parser.add_argument(
        '--days', 
        type=int, 
        default=7,
        help='수집할 일수 (기본값: 7)'
    )
    
    parser.add_argument(
        '--list-symbols',
        action='store_true',
        help='사용 가능한 코인 심볼 목록 출력'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Supabase 연결 테스트만 실행'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 데이터 삽입 없이 수집만 테스트'
    )
    
    return parser.parse_args()

def list_available_symbols(supabase_client: SupabaseClient, logger):
    """사용 가능한 코인 심볼 목록 출력"""
    try:
        crypto_list = supabase_client.get_crypto_list()
        
        if not crypto_list:
            logger.warning("사용 가능한 코인이 없습니다")
            return
        
        print("\n=== 사용 가능한 코인 목록 ===")
        for crypto in crypto_list:
            print(f"  {crypto['symbol']:4} - {crypto['name']}")
            if crypto.get('coingecko_id'):
                print(f"       CoinGecko: {crypto['coingecko_id']}")
        print()
        
    except Exception as e:
        log_error(logger, e, "코인 목록 조회")
        sys.exit(1)

def test_connection(supabase_client: SupabaseClient, logger):
    """연결 테스트"""
    logger.info("Supabase 연결 테스트 중...")
    
    if supabase_client.test_connection():
        logger.info("✅ Supabase 연결 성공")
        return True
    else:
        logger.error("❌ Supabase 연결 실패")
        return False

def collect_coingecko_data(symbol: str, days: int, dry_run: bool = False) -> bool:
    """
    CoinGecko 데이터 수집 및 저장
    
    Args:
        symbol: 코인 심볼
        days: 수집할 일수
        dry_run: 실제 삽입 없이 수집만 테스트
    
    Returns:
        성공 여부
    """
    # 로거 설정
    logger = setup_logger('dispersion_signal', Config.LOG_FILE, Config.LOG_LEVEL)
    
    try:
        # 설정 검증 (CoinGecko는 API 키가 선택사항)
        if not Config.SUPABASE_URL or not Config.SUPABASE_SERVICE_ROLE_KEY:
            logger.error("Supabase 설정이 필요합니다")
            return False
        
        # 클라이언트 초기화
        supabase_client = SupabaseClient(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        coingecko_collector = CoinGeckoCollector()  # API 키 없이도 사용 가능
        
        # 연결 테스트
        if not test_connection(supabase_client, logger):
            return False
        
        # 코인 ID 조회
        logger.info(f"코인 ID 조회 중: {symbol}")
        crypto_id = supabase_client.get_crypto_id(symbol)
        
        if not crypto_id:
            logger.error(f"코인을 찾을 수 없습니다: {symbol}")
            logger.info("사용 가능한 코인 목록을 확인하려면 --list-symbols 옵션을 사용하세요")
            return False
        
        logger.info(f"코인 ID 확인: {crypto_id}")
        
        # 날짜 범위 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"데이터 수집 기간: {start_date.strftime('%Y-%m-%d %H:%M')} ~ {end_date.strftime('%Y-%m-%d %H:%M')}")
        
        # CoinGecko 데이터 수집
        logger.info("CoinGecko에서 데이터 수집 중...")
        start_time = time.time()
        
        raw_data = coingecko_collector.collect_data(symbol, start_date, end_date)
        
        if not raw_data:
            logger.error("수집된 데이터가 없습니다")
            return False
        
        collection_time = time.time() - start_time
        log_data_collection(logger, symbol, len(raw_data), collection_time)
        
        if dry_run:
            logger.info("DRY RUN 모드: 데이터 수집 완료, 저장하지 않음")
            logger.info(f"수집된 데이터 샘플 (첫 3개):")
            for i, record in enumerate(raw_data[:3]):
                logger.info(f"  {i+1}. {record}")
            return True
        
        # 데이터 변환
        logger.info("데이터 변환 중...")
        market_metrics = []
        price_history = []
        
        for record in raw_data:
            try:
                # 타임스탬프 파싱
                timestamp = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                
                # MarketMetric 객체 생성 (시장 데이터)
                if 'current_price' in record:
                    metric = MarketMetric(
                        crypto_id=crypto_id,
                        timestamp=timestamp,
                        current_price=record.get('current_price'),
                        price_change_24h=record.get('price_change_24h'),
                        price_change_percentage_24h=record.get('price_change_percentage_24h'),
                        market_cap=record.get('market_cap'),
                        market_cap_change_24h=record.get('market_cap_change_24h'),
                        market_cap_change_percentage_24h=record.get('market_cap_change_percentage_24h'),
                        total_volume=record.get('total_volume'),
                        volume_change_24h=record.get('volume_change_24h'),
                        circulating_supply=record.get('circulating_supply'),
                        total_supply=record.get('total_supply'),
                        max_supply=record.get('max_supply'),
                        market_cap_rank=record.get('market_cap_rank'),
                        price_change_percentage_7d=record.get('price_change_percentage_7d'),
                        price_change_percentage_30d=record.get('price_change_percentage_30d'),
                        price_change_percentage_1y=record.get('price_change_percentage_1y'),
                        trust_score=record.get('trust_score'),
                        trade_volume_24h=record.get('trade_volume_24h'),
                        data_source='coingecko',
                        raw_data=record.get('raw_data', {})
                    )
                    market_metrics.append(metric)
                
                # PriceHistory 객체 생성 (가격 히스토리)
                if 'price' in record:
                    price_record = PriceHistory(
                        crypto_id=crypto_id,
                        timestamp=timestamp,
                        price=record['price'],
                        volume=record.get('volume'),
                        market_cap=record.get('market_cap'),
                        data_source='coingecko',
                        raw_data=record.get('raw_data', {})
                    )
                    price_history.append(price_record)
                
            except Exception as e:
                log_error(logger, e, f"데이터 변환 실패: {record}")
                continue
        
        if not market_metrics and not price_history:
            logger.error("변환된 데이터가 없습니다")
            return False
        
        # Supabase에 저장
        success_count = 0
        
        if market_metrics:
            logger.info(f"Supabase에 시장 메트릭 {len(market_metrics)}개 레코드 저장 중...")
            if supabase_client.insert_market_metrics(market_metrics):
                logger.info("✅ 시장 메트릭 저장 완료")
                success_count += len(market_metrics)
            else:
                logger.error("❌ 시장 메트릭 저장 실패")
        
        if price_history:
            logger.info(f"Supabase에 가격 히스토리 {len(price_history)}개 레코드 저장 중...")
            if supabase_client.insert_price_history(price_history):
                logger.info("✅ 가격 히스토리 저장 완료")
                success_count += len(price_history)
            else:
                logger.error("❌ 가격 히스토리 저장 실패")
        
        if success_count > 0:
            logger.info(f"🎉 총 {success_count}개 레코드 저장 완료!")
            
            # 최신 데이터 확인
            latest_data = supabase_client.get_latest_market_metrics(crypto_id, 5)
            if latest_data:
                logger.info("최신 저장된 데이터 (상위 5개):")
                for record in latest_data:
                    timestamp = record['timestamp']
                    price = record.get('current_price', 'N/A')
                    market_cap = record.get('market_cap', 'N/A')
                    logger.info(f"  {timestamp}: 가격=${price}, 시가총액=${market_cap}")
            
            return True
        else:
            logger.error("❌ 모든 데이터 저장 실패")
            return False
            
    except Exception as e:
        log_error(logger, e, "데이터 수집 프로세스")
        return False

def main():
    """메인 함수"""
    args = parse_arguments()
    
    # 로거 설정
    logger = setup_logger('dispersion_signal', Config.LOG_FILE, Config.LOG_LEVEL)
    
    logger.info("=" * 50)
    logger.info("Dispersion Signal - CoinGecko 데이터 수집기 시작 (무료)")
    logger.info("=" * 50)
    
    try:
        # Supabase 클라이언트 초기화
        supabase_client = SupabaseClient(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        
        # 코인 목록 출력
        if args.list_symbols:
            list_available_symbols(supabase_client, logger)
            return
        
        # 연결 테스트만 실행
        if args.test_connection:
            test_connection(supabase_client, logger)
            return
        
        # 데이터 수집 실행
        success = collect_coingecko_data(
            symbol=args.symbol,
            days=args.days,
            dry_run=args.dry_run
        )
        
        if success:
            logger.info("🎉 데이터 수집 완료!")
            sys.exit(0)
        else:
            logger.error("💥 데이터 수집 실패!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
        sys.exit(1)
    except Exception as e:
        log_error(logger, e, "메인 프로세스")
        sys.exit(1)

if __name__ == "__main__":
    main()
