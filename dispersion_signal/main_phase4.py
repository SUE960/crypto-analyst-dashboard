#!/usr/bin/env python3
"""
Dispersion Signal - Phase 4 다중 소스 데이터 연동 및 감성 분석
"""
import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime, timezone
from typing import List, Dict, Any
from uuid import UUID
from decimal import Decimal

# 프로젝트 모듈 임포트
from config import Config
from collectors.coincap import CoinCapCollector
from collectors.coinpaprika import CoinPaprikaCollector
from collectors.coingecko import CoinGeckoCollector
from collectors.reddit import RedditCollector
from analysis.dispersion_calculator import DispersionCalculator
from database.supabase_client_phase4 import SupabaseClientPhase4
from database.models_phase4 import MultiSourcePrice, RedditSentiment, EnhancedDispersionSignal
from utils.logger import setup_logger, log_error

def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='Phase 4: 다중 소스 데이터 연동 및 감성 분석',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main_phase4.py --collect-prices --coins 20
  python main_phase4.py --analyze-sentiment --coins 20
  python main_phase4.py --calculate-dispersion --coins 20
  python main_phase4.py --mode all --coins 20
  python main_phase4.py --test-connection
        """
    )
    
    parser.add_argument(
        '--collect-prices',
        action='store_true',
        help='다중 소스 가격 수집'
    )
    
    parser.add_argument(
        '--analyze-sentiment',
        action='store_true',
        help='Reddit 감성 분석'
    )
    
    parser.add_argument(
        '--calculate-dispersion',
        action='store_true',
        help='향상된 분산도 계산'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['all', 'prices', 'sentiment', 'dispersion'],
        help='실행 모드'
    )
    
    parser.add_argument(
        '--coins', 
        type=int, 
        default=20,
        help='분석할 코인 수 (기본값: 20)'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='API 연결 테스트만 실행'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 데이터 삽입 없이 계산만 테스트'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='조회할 레코드 수 (기본값: 50)'
    )
    
    return parser.parse_args()

def test_connection(supabase_client: SupabaseClientPhase4, logger):
    """연결 테스트"""
    logger.info("Phase 4 API 연결 테스트 중...")
    
    if supabase_client.test_connection():
        logger.info("✅ Supabase 연결 성공")
        
        # 데이터 요약 정보 출력
        summary = supabase_client.get_data_summary()
        if summary:
            logger.info("📊 데이터베이스 요약:")
            logger.info(f"  - 총 코인 수: {summary.get('total_coins', 0)}")
            logger.info(f"  - 다중 소스 가격: {summary.get('total_multi_source_prices', 0)}개 레코드")
            logger.info(f"  - Reddit 감성: {summary.get('total_reddit_sentiment', 0)}개 레코드")
            logger.info(f"  - 향상된 분산도 신호: {summary.get('total_enhanced_signals', 0)}개 레코드")
            logger.info(f"  - 기존 분산도 신호: {summary.get('total_dispersion_signals', 0)}개 레코드")
        
        return True
    else:
        logger.error("❌ Supabase 연결 실패")
        return False

def collect_multi_source_prices(symbols: List[str], supabase_client: SupabaseClientPhase4, 
                               dry_run: bool, logger) -> bool:
    """
    다중 소스 가격 수집
    
    Args:
        symbols: 코인 심볼 리스트
        supabase_client: Supabase 클라이언트
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info(f"다중 소스 가격 수집 시작: {len(symbols)}개 코인")
        
        # Collector 초기화 (CoinCap은 네트워크 연결 문제로 일시 제외)
        # coincap = CoinCapCollector()
        coinpaprika = CoinPaprikaCollector()
        coingecko = CoinGeckoCollector()
        
        multi_source_prices = []
        timestamp = datetime.now(timezone.utc)
        
        for symbol in symbols:
            try:
                # crypto_id 조회
                crypto_id = supabase_client.get_crypto_id(symbol)
                if not crypto_id:
                    logger.warning(f"crypto_id를 찾을 수 없습니다: {symbol}")
                    continue
                
                # 소스별 가격 수집
                prices = []
                price_data = {}
                
                # CoinCap 가격 (네트워크 연결 문제로 일시 제외)
                # try:
                #     coincap_price = coincap.get_coin_price(symbol.lower())
                #     if coincap_price:
                #         prices.append(Decimal(str(coincap_price)))
                #         price_data['coincap_price'] = Decimal(str(coincap_price))
                #         logger.info(f"  CoinCap {symbol}: ${coincap_price}")
                # except Exception as e:
                #     logger.warning(f"CoinCap 가격 수집 실패 {symbol}: {e}")
                
                # CoinPaprika 가격
                try:
                    coinpaprika_price = coinpaprika.get_coin_price_by_symbol(symbol)
                    if coinpaprika_price:
                        prices.append(Decimal(str(coinpaprika_price)))
                        price_data['coinpaprika_price'] = Decimal(str(coinpaprika_price))
                        logger.info(f"  CoinPaprika {symbol}: ${coinpaprika_price}")
                except Exception as e:
                    logger.warning(f"CoinPaprika 가격 수집 실패 {symbol}: {e}")
                
                # CoinGecko 가격
                try:
                    coingecko_price = coingecko.get_coin_price_by_symbol(symbol)
                    if coingecko_price:
                        prices.append(Decimal(str(coingecko_price)))
                        price_data['coingecko_price'] = Decimal(str(coingecko_price))
                        logger.info(f"  CoinGecko {symbol}: ${coingecko_price}")
                except Exception as e:
                    logger.warning(f"CoinGecko 가격 수집 실패 {symbol}: {e}")
                
                # 가격 이상치 필터링 (너무 작거나 큰 값 제거)
                filtered_prices = []
                for price in prices:
                    # BTC의 경우 $1,000 이상, ETH의 경우 $100 이상, USDC의 경우 $0.1 이상
                    min_price = Decimal('1000') if symbol == 'BTC' else Decimal('100') if symbol == 'ETH' else Decimal('0.1')
                    if price >= min_price:
                        filtered_prices.append(price)
                
                if len(filtered_prices) < 2:
                    logger.warning(f"필터링 후 충분한 가격 데이터가 없습니다: {symbol} ({len(filtered_prices)}개 소스)")
                    continue
                
                prices = filtered_prices
                
                # 통계 계산
                price_avg = sum(prices) / len(prices)
                price_max = max(prices)
                price_min = min(prices)
                price_dispersion = ((price_max - price_min) / price_avg * 100) if price_avg > 0 else Decimal(0)
                
                # MultiSourcePrice 모델 생성
                multi_price = MultiSourcePrice(
                    crypto_id=crypto_id,
                    timestamp=timestamp,
                    binance_price=None,  # 기존 데이터에서 가져올 예정
                    coinmarketcap_price=None,  # 기존 데이터에서 가져올 예정
                    coincap_price=price_data.get('coincap_price'),
                    coinpaprika_price=price_data.get('coinpaprika_price'),
                    coingecko_price=price_data.get('coingecko_price'),
                    price_sources_count=len(prices),
                    price_avg=price_avg,
                    price_dispersion=price_dispersion,
                    raw_data={
                        'symbol': symbol,
                        'prices': [float(p) for p in prices],
                        'sources': ['coincap', 'coinpaprika', 'coingecko']
                    }
                )
                
                multi_source_prices.append(multi_price)
                
                logger.info(f"  {symbol}: 평균가격=${price_avg:.2f}, 분산도={price_dispersion:.2f}%, 소스수={len(prices)}")
                
            except Exception as e:
                log_error(logger, e, f"다중 소스 가격 수집 실패: {symbol}")
                continue
        
        logger.info(f"✅ 다중 소스 가격 {len(multi_source_prices)}개 수집 완료")
        
        if dry_run:
            logger.info("DRY RUN 모드: 수집 완료, 저장하지 않음")
            return True
        
        # 데이터베이스에 저장
        if multi_source_prices:
            if supabase_client.insert_multi_source_prices(multi_source_prices):
                logger.info(f"✅ 다중 소스 가격 {len(multi_source_prices)}개 저장 완료")
                return True
            else:
                logger.error("❌ 다중 소스 가격 저장 실패")
                return False
        
        return False
        
    except Exception as e:
        log_error(logger, e, "다중 소스 가격 수집 프로세스")
        return False

def analyze_reddit_sentiment(symbols: List[str], supabase_client: SupabaseClientPhase4,
                           dry_run: bool, logger) -> bool:
    """
    Reddit 감성 분석
    
    Args:
        symbols: 코인 심볼 리스트
        supabase_client: Supabase 클라이언트
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info(f"Reddit 감성 분석 시작: {len(symbols)}개 코인")
        
        # Reddit Collector 초기화
        reddit = RedditCollector(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            username=Config.REDDIT_USERNAME,
            password=Config.REDDIT_PASSWORD,
            user_agent=Config.REDDIT_USER_AGENT
        )
        
        sentiments = []
        timestamp = datetime.now(timezone.utc)
        
        # 암호화폐 언급 분석
        crypto_mentions = reddit.get_crypto_mentions(symbols)
        
        for symbol, mentions in crypto_mentions.items():
            try:
                # crypto_id 조회
                crypto_id = supabase_client.get_crypto_id(symbol)
                if not crypto_id:
                    logger.warning(f"crypto_id를 찾을 수 없습니다: {symbol}")
                    continue
                
                # 감성 점수 계산
                sentiment_counts = {
                    'positive': mentions['positive_mentions'],
                    'negative': mentions['negative_mentions'],
                    'neutral': mentions['neutral_mentions']
                }
                
                sentiment_score = reddit.calculate_sentiment_score(sentiment_counts)
                
                # 커뮤니티 관심도 계산 (총 언급 수 기반)
                community_interest = min(mentions['total_mentions'] * 2, 100)  # 최대 100
                
                # RedditSentiment 모델 생성
                sentiment = RedditSentiment(
                    crypto_id=crypto_id,
                    timestamp=timestamp,
                    total_mentions=mentions['total_mentions'],
                    positive_mentions=mentions['positive_mentions'],
                    negative_mentions=mentions['negative_mentions'],
                    neutral_mentions=mentions['neutral_mentions'],
                    subreddit_breakdown=mentions['subreddit_breakdown'],
                    sentiment_score=Decimal(str(sentiment_score)),
                    community_interest=Decimal(str(community_interest)),
                    raw_data={
                        'symbol': symbol,
                        'mentions': mentions,
                        'sentiment_counts': sentiment_counts
                    }
                )
                
                sentiments.append(sentiment)
                
                logger.info(f"  {symbol}: 총언급={mentions['total_mentions']}, 감성점수={sentiment_score:.1f}, 관심도={community_interest:.1f}")
                
            except Exception as e:
                log_error(logger, e, f"Reddit 감성 분석 실패: {symbol}")
                continue
        
        logger.info(f"✅ Reddit 감성 분석 {len(sentiments)}개 완료")
        
        if dry_run:
            logger.info("DRY RUN 모드: 분석 완료, 저장하지 않음")
            return True
        
        # 데이터베이스에 저장
        if sentiments:
            if supabase_client.insert_reddit_sentiment(sentiments):
                logger.info(f"✅ Reddit 감성 데이터 {len(sentiments)}개 저장 완료")
                return True
            else:
                logger.error("❌ Reddit 감성 데이터 저장 실패")
                return False
        
        return False
        
    except Exception as e:
        log_error(logger, e, "Reddit 감성 분석 프로세스")
        return False

def calculate_enhanced_dispersion(symbols: List[str], supabase_client: SupabaseClientPhase4,
                                dry_run: bool, logger) -> bool:
    """
    향상된 분산도 계산
    
    Args:
        symbols: 코인 심볼 리스트
        supabase_client: Supabase 클라이언트
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info(f"향상된 분산도 계산 시작: {len(symbols)}개 코인")
        
        calculator = DispersionCalculator()
        enhanced_signals = []
        timestamp = datetime.now(timezone.utc)
        
        for symbol in symbols:
            try:
                # crypto_id 조회
                crypto_id = supabase_client.get_crypto_id(symbol)
                if not crypto_id:
                    logger.warning(f"crypto_id를 찾을 수 없습니다: {symbol}")
                    continue
                
                # 최신 다중 소스 가격 조회
                multi_prices = supabase_client.get_latest_multi_source_prices(crypto_id, limit=1)
                if not multi_prices:
                    logger.warning(f"다중 소스 가격 데이터가 없습니다: {symbol}")
                    continue
                
                latest_price = multi_prices[0]
                
                # 최신 Reddit 감성 조회
                reddit_sentiments = supabase_client.get_latest_reddit_sentiment(crypto_id, limit=1)
                reddit_sentiment_score = None
                reddit_mention_count = None
                
                if reddit_sentiments:
                    latest_sentiment = reddit_sentiments[0]
                    reddit_sentiment_score = Decimal(str(latest_sentiment.get('sentiment_score', 0)))
                    reddit_mention_count = latest_sentiment.get('total_mentions', 0)
                
                # 향상된 분산도 계산
                price_dispersion = Decimal(str(latest_price.get('price_dispersion', 0)))
                price_sources = latest_price.get('price_sources_count', 0)
                
                # 신호 레벨 및 타입 계산
                signal_level, signal_type = calculator.calculate_signal_level(
                    price_dispersion, Decimal(0), Decimal(0)  # 단순화
                )
                
                # 신뢰도 점수 계산 (다중 소스 + 감성 데이터 기반)
                confidence_score = Decimal(0)
                
                # 가격 소스 기반 신뢰도 (0-60점)
                if price_sources >= 5:
                    confidence_score += Decimal(60)
                elif price_sources >= 4:
                    confidence_score += Decimal(50)
                elif price_sources >= 3:
                    confidence_score += Decimal(40)
                elif price_sources >= 2:
                    confidence_score += Decimal(30)
                else:
                    confidence_score += Decimal(20)
                
                # Reddit 감성 기반 신뢰도 (0-40점)
                if reddit_sentiment_score is not None and reddit_mention_count is not None:
                    if reddit_mention_count > 50:
                        confidence_score += Decimal(40)
                    elif reddit_mention_count > 20:
                        confidence_score += Decimal(30)
                    elif reddit_mention_count > 10:
                        confidence_score += Decimal(20)
                    else:
                        confidence_score += Decimal(10)
                
                # EnhancedDispersionSignal 모델 생성
                enhanced_signal = EnhancedDispersionSignal(
                    crypto_id=crypto_id,
                    timestamp=timestamp,
                    price_dispersion=price_dispersion,
                    price_sources=price_sources,
                    reddit_sentiment_score=reddit_sentiment_score,
                    reddit_mention_count=reddit_mention_count,
                    signal_level=signal_level,
                    signal_type=signal_type,
                    confidence_score=confidence_score,
                    data_sources=['coincap', 'coinpaprika', 'coingecko', 'reddit'],
                    raw_data={
                        'symbol': symbol,
                        'multi_price_data': latest_price,
                        'reddit_sentiment_data': latest_sentiment if reddit_sentiments else None
                    }
                )
                
                enhanced_signals.append(enhanced_signal)
                
                logger.info(f"  {symbol}: 분산도={price_dispersion:.2f}%, 신호레벨={signal_level}, 신뢰도={confidence_score:.1f}%")
                
            except Exception as e:
                log_error(logger, e, f"향상된 분산도 계산 실패: {symbol}")
                continue
        
        logger.info(f"✅ 향상된 분산도 신호 {len(enhanced_signals)}개 계산 완료")
        
        if dry_run:
            logger.info("DRY RUN 모드: 계산 완료, 저장하지 않음")
            return True
        
        # 데이터베이스에 저장
        if enhanced_signals:
            if supabase_client.insert_enhanced_dispersion_signals(enhanced_signals):
                logger.info(f"✅ 향상된 분산도 신호 {len(enhanced_signals)}개 저장 완료")
                return True
            else:
                logger.error("❌ 향상된 분산도 신호 저장 실패")
                return False
        
        return False
        
    except Exception as e:
        log_error(logger, e, "향상된 분산도 계산 프로세스")
        return False

def main():
    """메인 함수"""
    args = parse_arguments()
    
    # 로거 설정
    logger = setup_logger('dispersion_signal_phase4', Config.LOG_FILE, Config.LOG_LEVEL)
    
    logger.info("=" * 60)
    logger.info("Dispersion Signal - Phase 4 다중 소스 데이터 연동 및 감성 분석")
    logger.info("=" * 60)
    
    try:
        # 설정 검증
        Config.validate()
        
        # 클라이언트 초기화
        supabase_client = SupabaseClientPhase4(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        
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
        logger.info(f"분석 대상 코인: {symbols}")
        
        # 작업 실행
        success_count = 0
        
        if args.collect_prices or args.mode in ['all', 'prices']:
            logger.info("\n📊 다중 소스 가격 수집 시작...")
            if collect_multi_source_prices(symbols, supabase_client, args.dry_run, logger):
                success_count += 1
        
        if args.analyze_sentiment or args.mode in ['all', 'sentiment']:
            logger.info("\n📈 Reddit 감성 분석 시작...")
            if analyze_reddit_sentiment(symbols, supabase_client, args.dry_run, logger):
                success_count += 1
        
        if args.calculate_dispersion or args.mode in ['all', 'dispersion']:
            logger.info("\n🔍 향상된 분산도 계산 시작...")
            if calculate_enhanced_dispersion(symbols, supabase_client, args.dry_run, logger):
                success_count += 1
        
        # 결과 출력
        if success_count > 0:
            logger.info(f"\n🎉 Phase 4 작업 완료! ({success_count}개 작업 성공)")
            
            if not args.dry_run:
                # 최신 데이터 확인
                summary = supabase_client.get_data_summary()
                if summary:
                    logger.info("📊 최종 데이터베이스 상태:")
                    logger.info(f"  - 총 코인 수: {summary.get('total_coins', 0)}")
                    logger.info(f"  - 다중 소스 가격: {summary.get('total_multi_source_prices', 0)}개 레코드")
                    logger.info(f"  - Reddit 감성: {summary.get('total_reddit_sentiment', 0)}개 레코드")
                    logger.info(f"  - 향상된 분산도 신호: {summary.get('total_enhanced_signals', 0)}개 레코드")
            
            sys.exit(0)
        else:
            logger.error("\n💥 모든 작업 실패!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
        sys.exit(1)
    except Exception as e:
        log_error(logger, e, "메인 프로세스")
        sys.exit(1)

if __name__ == "__main__":
    main()
