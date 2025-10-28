#!/usr/bin/env python3
"""
Dispersion Signal - Binance API 데이터 수집기 (무료)
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
from collectors.binance import BinanceCollector
from database.supabase_client_binance import SupabaseClientBinance
from database.models_binance import (
    CryptocurrencyBinance, MarketDataDaily, PriceHistory, 
    CurrentPrice, TopCoin
)
from utils.logger import setup_logger, log_data_collection, log_error

def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='Binance API 암호화폐 데이터 수집기 (무료)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main_binance.py --mode daily --coins 20
  python main_binance.py --mode historical --coins 10 --days 365
  python main_binance.py --list-symbols
  python main_binance.py --test-connection
        """
    )
    
    parser.add_argument(
        '--mode', 
        type=str, 
        choices=['daily', 'historical', 'both'],
        default='daily',
        help='수집 모드: daily(일일), historical(히스토리컬), both(둘 다)'
    )
    
    parser.add_argument(
        '--coins', 
        type=int, 
        default=20,
        help='수집할 코인 수 (기본값: 20)'
    )
    
    parser.add_argument(
        '--days', 
        type=int, 
        default=365,
        help='히스토리컬 데이터 수집 일수 (기본값: 365)'
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
    
    parser.add_argument(
        '--backfill',
        action='store_true',
        help='과거 데이터 재수집'
    )
    
    return parser.parse_args()

def list_available_symbols(supabase_client: SupabaseClientBinance, logger):
    """사용 가능한 코인 심볼 목록 출력"""
    try:
        crypto_list = supabase_client.get_crypto_list()
        
        if not crypto_list:
            logger.warning("사용 가능한 코인이 없습니다")
            return
        
        print("\n=== 사용 가능한 코인 목록 ===")
        for crypto in crypto_list:
            print(f"  {crypto['symbol']:8} - {crypto['name']:20} (순위: {crypto.get('market_cap_rank', 'N/A')})")
            if crypto.get('binance_symbol'):
                print(f"       Binance: {crypto['binance_symbol']}")
        print()
        
    except Exception as e:
        log_error(logger, e, "코인 목록 조회")
        sys.exit(1)

def test_connection(supabase_client: SupabaseClientBinance, logger):
    """연결 테스트"""
    logger.info("Supabase 연결 테스트 중...")
    
    if supabase_client.test_connection():
        logger.info("✅ Supabase 연결 성공")
        
        # 데이터 요약 정보 출력
        summary = supabase_client.get_data_summary()
        if summary:
            logger.info("📊 데이터베이스 요약:")
            logger.info(f"  - 총 코인 수: {summary.get('total_coins', 0)}")
            logger.info(f"  - 일일 데이터: {summary.get('total_daily_records', 0)}개 레코드")
            logger.info(f"  - 히스토리컬 데이터: {summary.get('total_history_records', 0)}개 레코드")
            logger.info(f"  - 현재 가격: {summary.get('total_current_records', 0)}개 레코드")
        
        return True
    else:
        logger.error("❌ Supabase 연결 실패")
        return False

def collect_top_coins(binance_collector: BinanceCollector, supabase_client: SupabaseClientBinance, 
                     coins_count: int, logger) -> List[str]:
    """
    상위 코인 조회 및 데이터베이스 업데이트
    
    Args:
        binance_collector: Binance 수집기
        supabase_client: Supabase 클라이언트
        coins_count: 조회할 코인 수
        logger: 로거
    
    Returns:
        코인 심볼 리스트
    """
    try:
        logger.info(f"상위 {coins_count}개 코인 조회 중...")
        
        # Binance에서 상위 코인 조회
        top_coins = binance_collector.get_top_coins(coins_count)
        
        if not top_coins:
            logger.error("상위 코인 조회 실패")
            return []
        
        logger.info(f"✅ {len(top_coins)}개 코인 조회 완료")
        
        # TopCoin 모델로 변환
        top_coin_models = []
        symbols = []
        
        for coin_data in top_coins:
            try:
                top_coin = TopCoin(
                    symbol=coin_data['symbol'],
                    name=coin_data['name'],
                    binance_symbol=coin_data['binance_symbol'],
                    market_cap_rank=coin_data['market_cap_rank'],
                    quote_volume=coin_data['quote_volume'],
                    last_price=coin_data['last_price'],
                    price_change_percent=coin_data['price_change_percent'],
                    raw_data=coin_data['raw_data']
                )
                top_coin_models.append(top_coin)
                symbols.append(coin_data['binance_symbol'])
                
            except Exception as e:
                log_error(logger, e, f"코인 데이터 변환 실패: {coin_data['symbol']}")
                continue
        
        # 데이터베이스에 업서트
        if top_coin_models:
            if supabase_client.upsert_cryptocurrencies(top_coin_models):
                logger.info(f"✅ 코인 마스터 데이터 {len(top_coin_models)}개 업서트 완료")
            else:
                logger.error("❌ 코인 마스터 데이터 업서트 실패")
        
        return symbols
        
    except Exception as e:
        log_error(logger, e, "상위 코인 수집")
        return []

def collect_daily_data(binance_collector: BinanceCollector, supabase_client: SupabaseClientBinance,
                      symbols: List[str], dry_run: bool, logger) -> bool:
    """
    일일 데이터 수집
    
    Args:
        binance_collector: Binance 수집기
        supabase_client: Supabase 클라이언트
        symbols: 코인 심볼 리스트
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info(f"일일 데이터 수집 시작: {len(symbols)}개 코인")
        
        # 일일 데이터 수집
        daily_data = binance_collector.collect_daily_data(symbols)
        
        if not daily_data:
            logger.error("일일 데이터 수집 실패")
            return False
        
        logger.info(f"✅ 일일 데이터 {len(daily_data)}개 수집 완료")
        
        if dry_run:
            logger.info("DRY RUN 모드: 데이터 수집 완료, 저장하지 않음")
            logger.info("수집된 데이터 샘플 (첫 3개):")
            for i, data in enumerate(daily_data[:3]):
                logger.info(f"  {i+1}. {data['symbol']}: 가격=${data['close_price']}, 거래량=${data['quote_volume']:,.0f}")
            return True
        
        # 데이터 변환 및 저장
        market_data_models = []
        
        for data in daily_data:
            try:
                # crypto_id 조회
                crypto_id = supabase_client.get_crypto_id(data['symbol'])
                if not crypto_id:
                    logger.warning(f"crypto_id를 찾을 수 없습니다: {data['symbol']}")
                    continue
                
                # MarketDataDaily 모델 생성
                market_data = MarketDataDaily(
                    crypto_id=crypto_id,
                    date=data['date'],
                    open_price=data['open_price'],
                    high_price=data['high_price'],
                    low_price=data['low_price'],
                    close_price=data['close_price'],
                    volume=data['volume'],
                    quote_volume=data['quote_volume'],
                    price_change_24h=data['price_change_24h'],
                    price_change_percent_24h=data['price_change_percent_24h'],
                    weighted_avg_price=data['weighted_avg_price'],
                    prev_close_price=data['prev_close_price'],
                    last_price=data['last_price'],
                    bid_price=data['bid_price'],
                    ask_price=data['ask_price'],
                    trade_count=data['trade_count'],
                    first_trade_id=data['first_trade_id'],
                    last_trade_id=data['last_trade_id'],
                    open_time=data['open_time'],
                    close_time=data['close_time'],
                    data_source='binance',
                    raw_data=data['raw_data']
                )
                
                market_data_models.append(market_data)
                
            except Exception as e:
                log_error(logger, e, f"일일 데이터 변환 실패: {data['symbol']}")
                continue
        
        # 데이터베이스에 저장
        if market_data_models:
            if supabase_client.insert_market_data_daily(market_data_models):
                logger.info(f"✅ 일일 시장 데이터 {len(market_data_models)}개 저장 완료")
                return True
            else:
                logger.error("❌ 일일 시장 데이터 저장 실패")
                return False
        
        return False
        
    except Exception as e:
        log_error(logger, e, "일일 데이터 수집 프로세스")
        return False

def collect_historical_data(binance_collector: BinanceCollector, supabase_client: SupabaseClientBinance,
                          symbols: List[str], days: int, dry_run: bool, logger) -> bool:
    """
    히스토리컬 데이터 수집
    
    Args:
        binance_collector: Binance 수집기
        supabase_client: Supabase 클라이언트
        symbols: 코인 심볼 리스트
        days: 수집할 일수
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info(f"히스토리컬 데이터 수집 시작: {len(symbols)}개 코인, {days}일")
        
        # 히스토리컬 데이터 수집
        historical_data = binance_collector.collect_historical_data(symbols, days)
        
        if not historical_data:
            logger.error("히스토리컬 데이터 수집 실패")
            return False
        
        logger.info(f"✅ 히스토리컬 데이터 {len(historical_data)}개 수집 완료")
        
        if dry_run:
            logger.info("DRY RUN 모드: 데이터 수집 완료, 저장하지 않음")
            logger.info("수집된 데이터 샘플 (첫 3개):")
            for i, data in enumerate(historical_data[:3]):
                logger.info(f"  {i+1}. {data['symbol']}: {data['timestamp']}, 가격=${data['close_price']}")
            return True
        
        # 데이터 변환 및 저장
        price_history_models = []
        
        for data in historical_data:
            try:
                # crypto_id 조회
                crypto_id = supabase_client.get_crypto_id(data['symbol'])
                if not crypto_id:
                    logger.warning(f"crypto_id를 찾을 수 없습니다: {data['symbol']}")
                    continue
                
                # PriceHistory 모델 생성
                price_history = PriceHistory(
                    crypto_id=crypto_id,
                    timestamp=data['timestamp'],
                    open_price=data['open_price'],
                    high_price=data['high_price'],
                    low_price=data['low_price'],
                    close_price=data['close_price'],
                    volume=data['volume'],
                    quote_volume=data['quote_volume'],
                    trade_count=data['trade_count'],
                    taker_buy_volume=data['taker_buy_volume'],
                    taker_buy_quote_volume=data['taker_buy_quote_volume'],
                    data_source='binance',
                    raw_data=data['raw_data']
                )
                
                price_history_models.append(price_history)
                
            except Exception as e:
                log_error(logger, e, f"히스토리컬 데이터 변환 실패: {data['symbol']}")
                continue
        
        # 데이터베이스에 저장
        if price_history_models:
            if supabase_client.insert_price_history(price_history_models):
                logger.info(f"✅ 히스토리컬 가격 데이터 {len(price_history_models)}개 저장 완료")
                return True
            else:
                logger.error("❌ 히스토리컬 가격 데이터 저장 실패")
                return False
        
        return False
        
    except Exception as e:
        log_error(logger, e, "히스토리컬 데이터 수집 프로세스")
        return False

def main():
    """메인 함수"""
    args = parse_arguments()
    
    # 로거 설정
    logger = setup_logger('dispersion_signal', Config.LOG_FILE, Config.LOG_LEVEL)
    
    logger.info("=" * 60)
    logger.info("Dispersion Signal - Binance API 데이터 수집기 시작 (무료)")
    logger.info("=" * 60)
    
    try:
        # 설정 검증
        Config.validate_binance()
        
        # 클라이언트 초기화
        supabase_client = SupabaseClientBinance(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        binance_collector = BinanceCollector()
        
        # 코인 목록 출력
        if args.list_symbols:
            list_available_symbols(supabase_client, logger)
            return
        
        # 연결 테스트만 실행
        if args.test_connection:
            test_connection(supabase_client, logger)
            return
        
        # 상위 코인 조회 및 업데이트
        symbols = collect_top_coins(binance_collector, supabase_client, args.coins, logger)
        
        if not symbols:
            logger.error("상위 코인 조회 실패")
            sys.exit(1)
        
        # 데이터 수집 실행
        success_count = 0
        
        if args.mode in ['daily', 'both']:
            logger.info("\n📊 일일 데이터 수집 시작...")
            if collect_daily_data(binance_collector, supabase_client, symbols, args.dry_run, logger):
                success_count += 1
        
        if args.mode in ['historical', 'both']:
            logger.info("\n📈 히스토리컬 데이터 수집 시작...")
            if collect_historical_data(binance_collector, supabase_client, symbols, args.days, args.dry_run, logger):
                success_count += 1
        
        # 결과 출력
        if success_count > 0:
            logger.info(f"\n🎉 데이터 수집 완료! ({success_count}개 모드 성공)")
            
            if not args.dry_run:
                # 최신 데이터 확인
                summary = supabase_client.get_data_summary()
                if summary:
                    logger.info("📊 최종 데이터베이스 상태:")
                    logger.info(f"  - 총 코인 수: {summary.get('total_coins', 0)}")
                    logger.info(f"  - 일일 데이터: {summary.get('total_daily_records', 0)}개 레코드")
                    logger.info(f"  - 히스토리컬 데이터: {summary.get('total_history_records', 0)}개 레코드")
            
            sys.exit(0)
        else:
            logger.error("\n💥 모든 데이터 수집 실패!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
        sys.exit(1)
    except Exception as e:
        log_error(logger, e, "메인 프로세스")
        sys.exit(1)

if __name__ == "__main__":
    main()
