#!/usr/bin/env python3
"""
Dispersion Signal - CryptoQuant 데이터 수집기
메인 실행 스크립트
"""
import argparse
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID

# 프로젝트 모듈 임포트
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from collectors.cryptoquant import CryptoQuantCollector
from database.supabase_client import SupabaseClient
from database.models import OnchainMetric
from utils.logger import setup_logger, log_data_collection, log_error

def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='CryptoQuant 온체인 데이터 수집기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main.py --symbol BTC --days 7 --interval 1hour
  python main.py --symbol ETH --days 3 --interval 4hour
  python main.py --list-symbols
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
        '--interval', 
        type=str, 
        default='1hour',
        choices=['1hour', '4hour', '1day'],
        help='데이터 간격 (기본값: 1hour)'
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
            if crypto.get('cryptoquant_ticker'):
                print(f"       CryptoQuant: {crypto['cryptoquant_ticker']}")
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

def collect_cryptoquant_data(symbol: str, days: int, interval: str, dry_run: bool = False) -> bool:
    """
    CryptoQuant 데이터 수집 및 저장
    
    Args:
        symbol: 코인 심볼
        days: 수집할 일수
        interval: 데이터 간격
        dry_run: 실제 삽입 없이 수집만 테스트
    
    Returns:
        성공 여부
    """
    # 로거 설정
    logger = setup_logger('dispersion_signal', Config.LOG_FILE, Config.LOG_LEVEL)
    
    try:
        # 설정 검증
        Config.validate()
        
        # 클라이언트 초기화
        supabase_client = SupabaseClient(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        cryptoquant_collector = CryptoQuantCollector(Config.CRYPTOQUANT_API_KEY)
        
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
        
        # CryptoQuant 데이터 수집
        logger.info("CryptoQuant에서 데이터 수집 중...")
        start_time = time.time()
        
        raw_data = cryptoquant_collector.collect_data(symbol, start_date, end_date, interval)
        
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
        onchain_metrics = []
        
        for record in raw_data:
            try:
                # 타임스탬프 파싱
                timestamp = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                
                # OnchainMetric 객체 생성
                metric = OnchainMetric(
                    crypto_id=crypto_id,
                    timestamp=timestamp,
                    exchange_netflow=record.get('exchange_netflow'),
                    exchange_reserve=record.get('exchange_reserve'),
                    active_addresses=record.get('active_addresses'),
                    miner_netflow=record.get('miner_netflow'),
                    transaction_count=record.get('transaction_count'),
                    transaction_volume=record.get('transaction_volume'),
                    data_source='cryptoquant',
                    raw_data=record.get('raw_data', {})
                )
                
                onchain_metrics.append(metric)
                
            except Exception as e:
                log_error(logger, e, f"데이터 변환 실패: {record}")
                continue
        
        if not onchain_metrics:
            logger.error("변환된 데이터가 없습니다")
            return False
        
        # Supabase에 저장
        logger.info(f"Supabase에 {len(onchain_metrics)}개 레코드 저장 중...")
        
        if supabase_client.insert_onchain_metrics(onchain_metrics):
            logger.info("✅ 데이터 저장 완료")
            
            # 최신 데이터 확인
            latest_data = supabase_client.get_latest_onchain_metrics(crypto_id, 5)
            if latest_data:
                logger.info("최신 저장된 데이터 (상위 5개):")
                for record in latest_data:
                    timestamp = record['timestamp']
                    netflow = record.get('exchange_netflow', 'N/A')
                    addresses = record.get('active_addresses', 'N/A')
                    logger.info(f"  {timestamp}: 넷플로우={netflow}, 활성주소={addresses}")
            
            return True
        else:
            logger.error("❌ 데이터 저장 실패")
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
    logger.info("Dispersion Signal - CryptoQuant 데이터 수집기 시작")
    logger.info("=" * 50)
    
    try:
        # 설정 검증
        Config.validate()
        
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
        success = collect_cryptoquant_data(
            symbol=args.symbol,
            days=args.days,
            interval=args.interval,
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
