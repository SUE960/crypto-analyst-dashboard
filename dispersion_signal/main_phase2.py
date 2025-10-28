#!/usr/bin/env python3
"""
Dispersion Signal - Phase 2 데이터 수집기
CoinMarketCap & CryptoCompare API 통합
"""
import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime, timezone
from typing import List, Dict, Any
from uuid import UUID

# 프로젝트 모듈 임포트
from config import Config
from collectors.coinmarketcap import CoinMarketCapCollector
from collectors.cryptocompare import CryptoCompareCollector
from database.supabase_client_phase2 import SupabaseClientPhase2
from database.models_phase2 import (
    MarketCapData, SocialData, NewsSentiment, GlobalMetrics
)
from utils.logger import setup_logger, log_data_collection, log_error

def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='Phase 2: CoinMarketCap & CryptoCompare API 데이터 수집기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main_phase2.py --mode marketcap --coins 20
  python main_phase2.py --mode social --coins 10
  python main_phase2.py --mode news --coins 5
  python main_phase2.py --mode global
  python main_phase2.py --mode all --coins 20
  python main_phase2.py --test-connection
        """
    )
    
    parser.add_argument(
        '--mode', 
        type=str, 
        choices=['marketcap', 'social', 'news', 'global', 'all'],
        default='marketcap',
        help='수집 모드: marketcap(시가총액), social(소셜), news(뉴스감성), global(글로벌), all(모든 모드)'
    )
    
    parser.add_argument(
        '--coins', 
        type=int, 
        default=20,
        help='수집할 코인 수 (기본값: 20)'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='API 연결 테스트만 실행'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 데이터 삽입 없이 수집만 테스트'
    )
    
    parser.add_argument(
        '--list-symbols',
        action='store_true',
        help='사용 가능한 코인 심볼 목록 출력'
    )
    
    return parser.parse_args()

def list_available_symbols(supabase_client: SupabaseClientPhase2, logger):
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

def test_connection(supabase_client: SupabaseClientPhase2, logger):
    """연결 테스트"""
    logger.info("Phase 2 API 연결 테스트 중...")
    
    if supabase_client.test_connection():
        logger.info("✅ Supabase 연결 성공")
        
        # 데이터 요약 정보 출력
        summary = supabase_client.get_data_summary()
        if summary:
            logger.info("📊 데이터베이스 요약:")
            logger.info(f"  - 총 코인 수: {summary.get('total_coins', 0)}")
            logger.info(f"  - 일일 데이터: {summary.get('total_daily_records', 0)}개 레코드")
            logger.info(f"  - 히스토리컬 데이터: {summary.get('total_history_records', 0)}개 레코드")
            logger.info(f"  - 시가총액 데이터: {summary.get('total_marketcap_records', 0)}개 레코드")
            logger.info(f"  - 소셜 데이터: {summary.get('total_social_records', 0)}개 레코드")
            logger.info(f"  - 뉴스 감성 데이터: {summary.get('total_news_records', 0)}개 레코드")
            logger.info(f"  - 글로벌 메트릭: {summary.get('total_global_records', 0)}개 레코드")
        
        return True
    else:
        logger.error("❌ Supabase 연결 실패")
        return False

def collect_market_cap_data(coinmarketcap_collector: CoinMarketCapCollector, 
                          supabase_client: SupabaseClientPhase2,
                          symbols: List[str], dry_run: bool, logger) -> bool:
    """
    시가총액 데이터 수집
    
    Args:
        coinmarketcap_collector: CoinMarketCap 수집기
        supabase_client: Supabase 클라이언트
        symbols: 코인 심볼 리스트
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info(f"시가총액 데이터 수집 시작: {len(symbols)}개 코인")
        
        # 시가총액 데이터 수집
        market_cap_data = coinmarketcap_collector.collect_market_cap_data(symbols)
        
        if not market_cap_data:
            logger.error("시가총액 데이터 수집 실패")
            return False
        
        logger.info(f"✅ 시가총액 데이터 {len(market_cap_data)}개 수집 완료")
        
        if dry_run:
            logger.info("DRY RUN 모드: 데이터 수집 완료, 저장하지 않음")
            logger.info("수집된 데이터 샘플 (첫 3개):")
            for i, data in enumerate(market_cap_data[:3]):
                logger.info(f"  {i+1}. {data['symbol']}: 시가총액=${data['market_cap']:,.0f}, 순위={data['market_cap_rank']}")
            return True
        
        # 데이터 변환 및 저장
        market_cap_models = []
        
        for data in market_cap_data:
            try:
                # crypto_id 조회
                crypto_id = supabase_client.get_crypto_id(data['symbol'])
                if not crypto_id:
                    logger.warning(f"crypto_id를 찾을 수 없습니다: {data['symbol']}")
                    continue
                
                # MarketCapData 모델 생성
                market_cap = MarketCapData(
                    crypto_id=crypto_id,
                    timestamp=data['timestamp'],
                    market_cap=data['market_cap'],
                    market_cap_rank=data['market_cap_rank'],
                    fully_diluted_market_cap=data['fully_diluted_market_cap'],
                    circulating_supply=data['circulating_supply'],
                    total_supply=data['total_supply'],
                    max_supply=data['max_supply'],
                    market_cap_dominance=data['market_cap_dominance'],
                    ath_price=data['ath_price'],
                    ath_date=data['ath_date'],
                    ath_change_percentage=data['ath_change_percentage'],
                    atl_price=data['atl_price'],
                    atl_date=data['atl_date'],
                    atl_change_percentage=data['atl_change_percentage'],
                    data_source='coinmarketcap',
                    raw_data=data['raw_data']
                )
                
                market_cap_models.append(market_cap)
                
            except Exception as e:
                log_error(logger, e, f"시가총액 데이터 변환 실패: {data['symbol']}")
                continue
        
        # 데이터베이스에 저장
        if market_cap_models:
            if supabase_client.insert_market_cap_data(market_cap_models):
                logger.info(f"✅ 시가총액 데이터 {len(market_cap_models)}개 저장 완료")
                return True
            else:
                logger.error("❌ 시가총액 데이터 저장 실패")
                return False
        
        return False
        
    except Exception as e:
        log_error(logger, e, "시가총액 데이터 수집 프로세스")
        return False

def collect_social_data(cryptocompare_collector: CryptoCompareCollector,
                       supabase_client: SupabaseClientPhase2,
                       symbols: List[str], dry_run: bool, logger) -> bool:
    """
    소셜 데이터 수집
    
    Args:
        cryptocompare_collector: CryptoCompare 수집기
        supabase_client: Supabase 클라이언트
        symbols: 코인 심볼 리스트
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info(f"소셜 데이터 수집 시작: {len(symbols)}개 코인")
        
        # 소셜 데이터 수집
        social_data = cryptocompare_collector.collect_social_data(symbols)
        
        if not social_data:
            logger.error("소셜 데이터 수집 실패")
            return False
        
        logger.info(f"✅ 소셜 데이터 {len(social_data)}개 수집 완료")
        
        if dry_run:
            logger.info("DRY RUN 모드: 데이터 수집 완료, 저장하지 않음")
            logger.info("수집된 데이터 샘플 (첫 3개):")
            for i, data in enumerate(social_data[:3]):
                logger.info(f"  {i+1}. 코인 ID {data['coin_id']}: 트위터 팔로워={data['twitter_followers']}, 레딧 구독자={data['reddit_subscribers']}")
            return True
        
        # 데이터 변환 및 저장
        social_models = []
        
        for data in social_data:
            try:
                # crypto_id 조회 (coin_id를 심볼로 변환 필요)
                # CryptoCompare는 coin_id를 사용하므로 직접 매핑 필요
                crypto_id = supabase_client.get_crypto_id(f"COIN_{data['coin_id']}")  # 임시 매핑
                if not crypto_id:
                    logger.warning(f"crypto_id를 찾을 수 없습니다: 코인 ID {data['coin_id']}")
                    continue
                
                # SocialData 모델 생성
                social = SocialData(
                    crypto_id=crypto_id,
                    timestamp=data['timestamp'],
                    twitter_followers=data['twitter_followers'],
                    twitter_following=data['twitter_following'],
                    twitter_lists=data['twitter_lists'],
                    twitter_favourites=data['twitter_favourites'],
                    twitter_statuses=data['twitter_statuses'],
                    reddit_subscribers=data['reddit_subscribers'],
                    reddit_active_users=data['reddit_active_users'],
                    reddit_posts_per_hour=data['reddit_posts_per_hour'],
                    reddit_comments_per_hour=data['reddit_comments_per_hour'],
                    community_score=data['community_score'],
                    public_interest_score=data['public_interest_score'],
                    data_source='cryptocompare',
                    raw_data=data['raw_data']
                )
                
                social_models.append(social)
                
            except Exception as e:
                log_error(logger, e, f"소셜 데이터 변환 실패: 코인 ID {data['coin_id']}")
                continue
        
        # 데이터베이스에 저장
        if social_models:
            if supabase_client.insert_social_data(social_models):
                logger.info(f"✅ 소셜 데이터 {len(social_models)}개 저장 완료")
                return True
            else:
                logger.error("❌ 소셜 데이터 저장 실패")
                return False
        
        return False
        
    except Exception as e:
        log_error(logger, e, "소셜 데이터 수집 프로세스")
        return False

def collect_news_sentiment_data(cryptocompare_collector: CryptoCompareCollector,
                               supabase_client: SupabaseClientPhase2,
                               symbols: List[str], dry_run: bool, logger) -> bool:
    """
    뉴스 감성 데이터 수집
    
    Args:
        cryptocompare_collector: CryptoCompare 수집기
        supabase_client: Supabase 클라이언트
        symbols: 코인 심볼 리스트
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info(f"뉴스 감성 데이터 수집 시작: {len(symbols)}개 코인")
        
        # 뉴스 감성 데이터 수집
        sentiment_data = cryptocompare_collector.collect_news_sentiment_data(symbols)
        
        if not sentiment_data:
            logger.error("뉴스 감성 데이터 수집 실패")
            return False
        
        logger.info(f"✅ 뉴스 감성 데이터 {len(sentiment_data)}개 수집 완료")
        
        if dry_run:
            logger.info("DRY RUN 모드: 데이터 수집 완료, 저장하지 않음")
            logger.info("수집된 데이터 샘플 (첫 3개):")
            for i, data in enumerate(sentiment_data[:3]):
                logger.info(f"  {i+1}. {data['symbol']}: 감성점수={data['sentiment_score']}, 뉴스수={data['news_count']}")
            return True
        
        # 데이터 변환 및 저장
        sentiment_models = []
        
        for data in sentiment_data:
            try:
                # crypto_id 조회
                crypto_id = supabase_client.get_crypto_id(data['symbol'])
                if not crypto_id:
                    logger.warning(f"crypto_id를 찾을 수 없습니다: {data['symbol']}")
                    continue
                
                # NewsSentiment 모델 생성
                sentiment = NewsSentiment(
                    crypto_id=crypto_id,
                    timestamp=data['timestamp'],
                    news_count=data['news_count'],
                    news_sources=data['news_sources'],
                    sentiment_score=data['sentiment_score'],
                    sentiment_positive=data['sentiment_positive'],
                    sentiment_neutral=data['sentiment_neutral'],
                    sentiment_negative=data['sentiment_negative'],
                    trending_score=data['trending_score'],
                    data_source='cryptocompare',
                    raw_data=data['raw_data']
                )
                
                sentiment_models.append(sentiment)
                
            except Exception as e:
                log_error(logger, e, f"뉴스 감성 데이터 변환 실패: {data['symbol']}")
                continue
        
        # 데이터베이스에 저장
        if sentiment_models:
            if supabase_client.insert_news_sentiment(sentiment_models):
                logger.info(f"✅ 뉴스 감성 데이터 {len(sentiment_models)}개 저장 완료")
                return True
            else:
                logger.error("❌ 뉴스 감성 데이터 저장 실패")
                return False
        
        return False
        
    except Exception as e:
        log_error(logger, e, "뉴스 감성 데이터 수집 프로세스")
        return False

def collect_global_metrics(coinmarketcap_collector: CoinMarketCapCollector,
                          supabase_client: SupabaseClientPhase2,
                          dry_run: bool, logger) -> bool:
    """
    글로벌 메트릭 데이터 수집
    
    Args:
        coinmarketcap_collector: CoinMarketCap 수집기
        supabase_client: Supabase 클라이언트
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info("글로벌 메트릭 데이터 수집 시작")
        
        # 글로벌 메트릭 데이터 수집
        global_data = coinmarketcap_collector.collect_global_metrics_data()
        
        if not global_data:
            logger.error("글로벌 메트릭 데이터 수집 실패")
            return False
        
        logger.info("✅ 글로벌 메트릭 데이터 수집 완료")
        
        if dry_run:
            logger.info("DRY RUN 모드: 데이터 수집 완료, 저장하지 않음")
            logger.info(f"수집된 글로벌 메트릭:")
            logger.info(f"  - 총 시가총액: ${global_data['total_market_cap']:,.0f}")
            logger.info(f"  - 총 거래량: ${global_data['total_volume_24h']:,.0f}")
            logger.info(f"  - BTC 도미넌스: {global_data['btc_dominance']:.2f}%")
            logger.info(f"  - ETH 도미넌스: {global_data['eth_dominance']:.2f}%")
            return True
        
        # 데이터 변환 및 저장
        try:
            # GlobalMetrics 모델 생성
            global_metrics = GlobalMetrics(
                timestamp=global_data['timestamp'],
                total_market_cap=global_data['total_market_cap'],
                total_volume_24h=global_data['total_volume_24h'],
                btc_dominance=global_data['btc_dominance'],
                eth_dominance=global_data['eth_dominance'],
                active_cryptocurrencies=global_data['active_cryptocurrencies'],
                active_exchanges=global_data['active_exchanges'],
                data_source='coinmarketcap',
                raw_data=global_data['raw_data']
            )
            
            # 데이터베이스에 저장
            if supabase_client.insert_global_metrics(global_metrics):
                logger.info("✅ 글로벌 메트릭 데이터 저장 완료")
                return True
            else:
                logger.error("❌ 글로벌 메트릭 데이터 저장 실패")
                return False
                
        except Exception as e:
            log_error(logger, e, "글로벌 메트릭 데이터 변환 실패")
            return False
        
    except Exception as e:
        log_error(logger, e, "글로벌 메트릭 데이터 수집 프로세스")
        return False

def main():
    """메인 함수"""
    args = parse_arguments()
    
    # 로거 설정
    logger = setup_logger('dispersion_signal_phase2', Config.LOG_FILE, Config.LOG_LEVEL)
    
    logger.info("=" * 60)
    logger.info("Dispersion Signal - Phase 2 데이터 수집기 시작")
    logger.info("CoinMarketCap & CryptoCompare API 통합")
    logger.info("=" * 60)
    
    try:
        # 설정 검증
        Config.validate_phase2()
        
        # 클라이언트 초기화
        supabase_client = SupabaseClientPhase2(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        coinmarketcap_collector = CoinMarketCapCollector(Config.COINMARKETCAP_API_KEY)
        cryptocompare_collector = CryptoCompareCollector(Config.CRYPTOCOMPARE_API_KEY)
        
        # 코인 목록 출력
        if args.list_symbols:
            list_available_symbols(supabase_client, logger)
            return
        
        # 연결 테스트만 실행
        if args.test_connection:
            test_connection(supabase_client, logger)
            return
        
        # 코인 심볼 조회
        crypto_list = supabase_client.get_crypto_list()
        if not crypto_list:
            logger.error("코인 목록을 조회할 수 없습니다")
            sys.exit(1)
        
        # 요청된 수만큼 코인 선택
        symbols = [crypto['symbol'] for crypto in crypto_list[:args.coins]]
        logger.info(f"수집 대상 코인: {symbols}")
        
        # 데이터 수집 실행
        success_count = 0
        
        if args.mode in ['marketcap', 'all']:
            logger.info("\n📊 시가총액 데이터 수집 시작...")
            if collect_market_cap_data(coinmarketcap_collector, supabase_client, symbols, args.dry_run, logger):
                success_count += 1
        
        if args.mode in ['social', 'all']:
            logger.info("\n📱 소셜 데이터 수집 시작...")
            if collect_social_data(cryptocompare_collector, supabase_client, symbols, args.dry_run, logger):
                success_count += 1
        
        if args.mode in ['news', 'all']:
            logger.info("\n📰 뉴스 감성 데이터 수집 시작...")
            if collect_news_sentiment_data(cryptocompare_collector, supabase_client, symbols, args.dry_run, logger):
                success_count += 1
        
        if args.mode in ['global', 'all']:
            logger.info("\n🌍 글로벌 메트릭 수집 시작...")
            if collect_global_metrics(coinmarketcap_collector, supabase_client, args.dry_run, logger):
                success_count += 1
        
        # 결과 출력
        if success_count > 0:
            logger.info(f"\n🎉 Phase 2 데이터 수집 완료! ({success_count}개 모드 성공)")
            
            if not args.dry_run:
                # 최신 데이터 확인
                summary = supabase_client.get_data_summary()
                if summary:
                    logger.info("📊 최종 데이터베이스 상태:")
                    logger.info(f"  - 총 코인 수: {summary.get('total_coins', 0)}")
                    logger.info(f"  - 시가총액 데이터: {summary.get('total_marketcap_records', 0)}개 레코드")
                    logger.info(f"  - 소셜 데이터: {summary.get('total_social_records', 0)}개 레코드")
                    logger.info(f"  - 뉴스 감성 데이터: {summary.get('total_news_records', 0)}개 레코드")
                    logger.info(f"  - 글로벌 메트릭: {summary.get('total_global_records', 0)}개 레코드")
            
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
