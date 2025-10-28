#!/usr/bin/env python3
"""
Dispersion Signal - 통합 개선된 데이터 수집 시스템
데이터 품질 검증, 모니터링, 백업, 성능 최적화 통합
"""
import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from decimal import Decimal

# 프로젝트 모듈 임포트
from config import Config
from collectors.binance import BinanceCollector
from collectors.coinmarketcap import CoinMarketCapCollector
from collectors.cryptocompare import CryptoCompareCollector
from collectors.coincap import CoinCapCollector
from collectors.coinpaprika import CoinPaprikaCollector
from collectors.coingecko import CoinGeckoCollector
from collectors.reddit import RedditCollector

from database.supabase_client_phase4 import SupabaseClientPhase4
from database.models_phase4 import MultiSourcePrice, RedditSentiment, EnhancedDispersionSignal

# 새로운 유틸리티 모듈들
from utils.data_quality import DataQualityValidator
from utils.monitoring import SystemMonitor, AlertConfig, AlertSeverity
from utils.backup import DataBackupManager, BackupConfig, BackupType
from utils.async_collector import OptimizedDataCollector, AsyncRequestConfig, CacheConfig
from utils.security import SecurityManager, SecurityConfig, APISecurityValidator

from utils.logger import setup_logger, log_data_collection, log_error

def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='Dispersion Signal - 통합 개선된 데이터 수집 시스템',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main_enhanced.py --mode all --coins 20 --enable-monitoring
  python main_enhanced.py --mode prices --coins 10 --enable-cache
  python main_enhanced.py --backup --backup-type full
  python main_enhanced.py --monitor-status
  python main_enhanced.py --quality-check --coins 5
        """
    )
    
    parser.add_argument(
        '--mode', 
        type=str, 
        choices=['prices', 'sentiment', 'dispersion', 'all'],
        default='all',
        help='수집 모드: prices(가격), sentiment(감성), dispersion(분산도), all(모든 모드)'
    )
    
    parser.add_argument(
        '--coins', 
        type=int, 
        default=20,
        help='수집할 코인 수 (기본값: 20)'
    )
    
    parser.add_argument(
        '--enable-monitoring',
        action='store_true',
        help='실시간 모니터링 활성화'
    )
    
    parser.add_argument(
        '--enable-cache',
        action='store_true',
        help='캐싱 시스템 활성화'
    )
    
    parser.add_argument(
        '--enable-backup',
        action='store_true',
        help='자동 백업 활성화'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        help='수동 백업 실행'
    )
    
    parser.add_argument(
        '--backup-type',
        type=str,
        choices=['full', 'incremental', 'differential'],
        default='full',
        help='백업 타입'
    )
    
    parser.add_argument(
        '--monitor-status',
        action='store_true',
        help='시스템 상태 확인'
    )
    
    parser.add_argument(
        '--quality-check',
        action='store_true',
        help='데이터 품질 검사 실행'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='연결 테스트만 실행'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='실제 저장 없이 테스트 실행'
    )
    
    parser.add_argument(
        '--async-mode',
        action='store_true',
        help='비동기 모드 활성화'
    )
    
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=10,
        help='최대 동시 요청 수 (비동기 모드)'
    )
    
    return parser.parse_args()

def initialize_enhanced_system(logger) -> Dict[str, Any]:
    """개선된 시스템 초기화"""
    logger.info("🔧 개선된 시스템 초기화 중...")
    
    # 데이터 품질 검증기
    quality_validator = DataQualityValidator(logger)
    
    # 모니터링 시스템
    alert_config = AlertConfig(
        email_enabled=False,  # 환경에 따라 설정
        slack_enabled=False,  # 환경에 따라 설정
        email_recipients=[],
        slack_webhook_url=""
    )
    monitor = SystemMonitor(alert_config, logger)
    
    # 백업 시스템
    backup_config = BackupConfig(
        backup_directory="backups",
        retention_days=30,
        compression_enabled=True
    )
    backup_manager = DataBackupManager(backup_config, logger)
    
    # 캐싱 시스템
    cache_config = CacheConfig(
        cache_directory="cache",
        max_cache_size_mb=100,
        default_ttl_seconds=300
    )
    
    # 비동기 수집기
    async_config = AsyncRequestConfig(
        max_concurrent_requests=10,
        request_timeout=30,
        retry_attempts=3
    )
    optimized_collector = OptimizedDataCollector(async_config, cache_config, logger)
    
    # 보안 시스템
    security_config = SecurityConfig()
    security_manager = SecurityManager(security_config, logger)
    
    return {
        'quality_validator': quality_validator,
        'monitor': monitor,
        'backup_manager': backup_manager,
        'optimized_collector': optimized_collector,
        'security_manager': security_manager
    }

async def collect_multi_source_prices_enhanced(symbols: List[str], supabase_client: SupabaseClientPhase4,
                                              enhanced_system: Dict[str, Any], dry_run: bool, logger) -> bool:
    """개선된 다중 소스 가격 수집"""
    logger.info(f"📊 개선된 다중 소스 가격 수집 시작: {len(symbols)}개 코인")
    
    quality_validator = enhanced_system['quality_validator']
    monitor = enhanced_system['monitor']
    optimized_collector = enhanced_system['optimized_collector']
    
    # 수집기 초기화
    coincap_collector = CoinCapCollector()
    coinpaprika_collector = CoinPaprikaCollector()
    coingecko_collector = CoinGeckoCollector()
    
    # 작동하는 API들 추가
    from collectors.binance import BinanceCollector
    from collectors.cryptocompare import CryptoCompareCollector
    from collectors.reddit import RedditCollector
    from config import Config
    
    binance_collector = BinanceCollector()
    cryptocompare_collector = CryptoCompareCollector(Config.CRYPTOCOMPARE_API_KEY)
    reddit_collector = RedditCollector(
        client_id=Config.REDDIT_CLIENT_ID,
        client_secret=Config.REDDIT_CLIENT_SECRET,
        username=Config.REDDIT_USERNAME,
        password=Config.REDDIT_PASSWORD,
        user_agent=Config.REDDIT_USER_AGENT
    )
    
    collected_data = []
    success_count = 0
    
    for symbol in symbols:
        try:
            logger.info(f"  {symbol} 가격 수집 중...")
            
            # 비동기 가격 수집
            prices = {}
            
            # CoinCap (DNS 문제로 임시 비활성화)
            # try:
            #     coincap_price = coincap_collector.get_coin_price(symbol)
            #     if coincap_price:
            #         prices['coincap'] = Decimal(str(coincap_price))
            #         monitor.monitor_api_call('coincap', True)
            #     else:
            #         monitor.monitor_api_call('coincap', False)
            # except Exception as e:
            #     monitor.monitor_api_call('coincap', False)
            #     logger.warning(f"CoinCap {symbol} 가격 수집 실패: {e}")
            
            # Binance API
            try:
                binance_data = binance_collector.get_current_price(symbol + 'USDT')
                if binance_data and 'data' in binance_data and 'price' in binance_data['data']:
                    prices['binance'] = Decimal(str(binance_data['data']['price']))
                    monitor.monitor_api_call('binance', True)
                else:
                    monitor.monitor_api_call('binance', False)
            except Exception as e:
                monitor.monitor_api_call('binance', False)
                logger.warning(f"Binance {symbol} 가격 수집 실패: {e}")
            
            # CryptoCompare API (가격 조회 메서드 없음으로 비활성화)
            # try:
            #     cryptocompare_price = cryptocompare_collector.get_price(symbol, 'USD')
            #     if cryptocompare_price:
            #         prices['cryptocompare'] = Decimal(str(cryptocompare_price))
            #         monitor.monitor_api_call('cryptocompare', True)
            #     else:
            #         monitor.monitor_api_call('cryptocompare', False)
            # except Exception as e:
            #     monitor.monitor_api_call('cryptocompare', False)
            #     logger.warning(f"CryptoCompare {symbol} 가격 수집 실패: {e}")
            
            # CoinPaprika (402 Payment Required로 임시 비활성화)
            # try:
            #     coinpaprika_price = coinpaprika_collector.get_coin_price_by_symbol(symbol)
            #     if coinpaprika_price:
            #         prices['coinpaprika'] = Decimal(str(coinpaprika_price))
            #         monitor.monitor_api_call('coinpaprika', True)
            #     else:
            #         monitor.monitor_api_call('coinpaprika', False)
            # except Exception as e:
            #     monitor.monitor_api_call('coinpaprika', False)
            #     logger.warning(f"CoinPaprika {symbol} 가격 수집 실패: {e}")
            
            # CoinGecko (Rate Limit 문제로 임시 비활성화)
            # try:
            #     coingecko_price = coingecko_collector.get_coin_price_by_symbol(symbol)
            #     if coingecko_price:
            #         prices['coingecko'] = Decimal(str(coingecko_price))
            #         monitor.monitor_api_call('coingecko', True)
            #     else:
            #         monitor.monitor_api_call('coingecko', False)
            # except Exception as e:
            #     monitor.monitor_api_call('coingecko', False)
            #     logger.warning(f"CoinGecko {symbol} 가격 수집 실패: {e}")
            
            # 추가 데이터 소스들 (가격이 아닌 다른 데이터)
            additional_data = {}
            
            # CryptoPanic 뉴스 데이터
            try:
                import requests
                import os
                from dotenv import load_dotenv
                load_dotenv()
                
                cryptopanic_key = os.getenv('CRYPTOPANIC_API_KEY')
                if cryptopanic_key:
                    response = requests.get(
                        f'https://cryptopanic.com/api/v1/posts/?auth_token={cryptopanic_key}&public=true&currencies={symbol}&limit=5',
                        timeout=10
                    )
                    if response.status_code == 200:
                        data = response.json()
                        additional_data['cryptopanic_news_count'] = len(data.get('results', []))
                        monitor.monitor_api_call('cryptopanic', True)
                    else:
                        monitor.monitor_api_call('cryptopanic', False)
            except Exception as e:
                monitor.monitor_api_call('cryptopanic', False)
                logger.warning(f"CryptoPanic {symbol} 뉴스 수집 실패: {e}")
            
            # Alternative.me Fear & Greed Index
            try:
                response = requests.get('https://api.alternative.me/fng/', timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and len(data['data']) > 0:
                        additional_data['fear_greed_index'] = int(data['data'][0]['value'])
                        monitor.monitor_api_call('alternative', True)
                    else:
                        monitor.monitor_api_call('alternative', False)
            except Exception as e:
                monitor.monitor_api_call('alternative', False)
                logger.warning(f"Alternative.me Fear & Greed Index 수집 실패: {e}")
            
            # 데이터 품질 검증
            is_valid, errors = quality_validator.validate_price_data(prices, symbol)
            
            if not is_valid:
                logger.warning(f"{symbol} 가격 데이터 품질 검증 실패: {errors}")
                continue
            
            # 품질 점수 계산
            quality_score = quality_validator.get_data_quality_score(prices)
            monitor.monitor_data_quality(symbol, quality_score)
            
            if len(prices) >= 2:
                # 통계 계산
                price_values = list(prices.values())
                avg_price = sum(price_values) / len(price_values)
                
                # Decimal 연산을 위한 표준편차 계산
                variance = sum((p - avg_price) ** 2 for p in price_values) / len(price_values)
                std_dev = variance ** Decimal('0.5')
                dispersion = (std_dev / avg_price) * 100 if avg_price > 0 else Decimal('0')
                
                # 분산도 모니터링
                monitor.monitor_price_dispersion(symbol, float(dispersion))
                
                crypto_id = supabase_client.get_crypto_id(symbol)
                if crypto_id:
                    multi_source_price = MultiSourcePrice(
                        crypto_id=crypto_id,
                        timestamp=datetime.now(timezone.utc),
                        coincap_price=prices.get('coincap'),
                        coinpaprika_price=prices.get('coinpaprika'),
                        coingecko_price=prices.get('coingecko'),
                        price_sources_count=len(prices),
                        price_avg=avg_price,
                        price_std_dev=std_dev,
                        price_dispersion=dispersion,
                        raw_data={'prices': {k: str(v) for k, v in prices.items()}}
                    )
                    
                    collected_data.append(multi_source_price)
                    success_count += 1
                    
                    logger.info(f"  {symbol}: 평균가격=${avg_price:.2f}, 분산도={dispersion:.2f}%, 소스수={len(prices)}")
            
        except Exception as e:
            log_error(logger, e, f"가격 수집 실패: {symbol}")
    
    logger.info(f"✅ 다중 소스 가격 {success_count}개 수집 완료")
    
    if not dry_run and collected_data:
        # Supabase에 저장
        for data in collected_data:
            supabase_client.insert_multi_source_price(data)
        logger.info(f"✅ 다중 소스 가격 {len(collected_data)}개 저장 완료")
    
    return success_count > 0

async def analyze_reddit_sentiment_enhanced(symbols: List[str], supabase_client: SupabaseClientPhase4,
                                         enhanced_system: Dict[str, Any], dry_run: bool, logger) -> bool:
    """개선된 Reddit 감성 분석"""
    logger.info(f"📈 개선된 Reddit 감성 분석 시작: {len(symbols)}개 코인")
    
    quality_validator = enhanced_system['quality_validator']
    monitor = enhanced_system['monitor']
    
    try:
        # Reddit 수집기 초기화
        reddit_collector = RedditCollector(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            username=Config.REDDIT_USERNAME,
            password=Config.REDDIT_PASSWORD,
            user_agent=Config.REDDIT_USER_AGENT
        )
        
        collected_data = []
        success_count = 0
        
        for symbol in symbols:
            try:
                logger.info(f"  {symbol} 감성 분석 중...")
                
                # Reddit 감성 분석
                crypto_mentions = reddit_collector.get_crypto_mentions([symbol])
                
                if symbol in crypto_mentions:
                    mention_data = crypto_mentions[symbol]
                    total_mentions = mention_data['total_mentions']
                    positive_mentions = mention_data['positive_mentions']
                    negative_mentions = mention_data['negative_mentions']
                    neutral_mentions = mention_data['neutral_mentions']
                    
                    # 감성 점수 계산
                    if total_mentions > 0:
                        sentiment_score = ((positive_mentions - negative_mentions) / total_mentions) * 100
                        community_interest = min(100, (total_mentions / 10) * 100)  # 정규화
                    else:
                        sentiment_score = Decimal('0')
                        community_interest = Decimal('0')
                    
                    # 데이터 품질 검증
                    is_valid, errors = quality_validator.validate_sentiment_data(
                        Decimal(str(sentiment_score)), total_mentions, symbol
                    )
                    
                    if not is_valid:
                        logger.warning(f"{symbol} 감성 데이터 품질 검증 실패: {errors}")
                        continue
                    
                    crypto_id = supabase_client.get_crypto_id(symbol)
                    if crypto_id:
                        reddit_sentiment = RedditSentiment(
                            crypto_id=crypto_id,
                            timestamp=datetime.now(timezone.utc),
                            total_mentions=total_mentions,
                            positive_mentions=positive_mentions,
                            negative_mentions=negative_mentions,
                            neutral_mentions=neutral_mentions,
                            subreddit_breakdown=mention_data['subreddit_breakdown'],
                            sentiment_score=Decimal(str(sentiment_score)),
                            community_interest=Decimal(str(community_interest)),
                            raw_data=mention_data
                        )
                        
                        collected_data.append(reddit_sentiment)
                        success_count += 1
                        
                        logger.info(f"  {symbol}: 총언급={total_mentions}, 감성점수={sentiment_score:.1f}, 관심도={community_interest:.1f}")
                
            except Exception as e:
                log_error(logger, e, f"감성 분석 실패: {symbol}")
        
        logger.info(f"✅ Reddit 감성 분석 {success_count}개 완료")
        
        if not dry_run and collected_data:
            # Supabase에 저장
            for data in collected_data:
                supabase_client.insert_reddit_sentiment(data)
            logger.info(f"✅ Reddit 감성 데이터 {len(collected_data)}개 저장 완료")
        
        return success_count > 0
        
    except Exception as e:
        log_error(logger, e, "Reddit 감성 분석")
        return False

def create_backup(enhanced_system: Dict[str, Any], backup_type: str, logger) -> bool:
    """백업 생성"""
    logger.info(f"💾 {backup_type} 백업 생성 시작...")
    
    backup_manager = enhanced_system['backup_manager']
    
    try:
        # 현재 데이터베이스 상태 수집
        backup_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'backup_type': backup_type,
            'system_info': {
                'python_version': sys.version,
                'platform': os.name
            },
            'config': {
                'coins_count': 20,
                'enabled_features': ['monitoring', 'quality_check', 'backup']
            }
        }
        
        # 백업 타입 결정
        if backup_type == 'full':
            backup_type_enum = BackupType.FULL
        elif backup_type == 'incremental':
            backup_type_enum = BackupType.INCREMENTAL
        else:
            backup_type_enum = BackupType.DIFFERENTIAL
        
        # 백업 생성
        backup_path = backup_manager.create_backup(backup_data, backup_type_enum)
        
        if backup_path:
            logger.info(f"✅ 백업 생성 완료: {backup_path}")
            
            # 백업 통계 출력
            stats = backup_manager.get_backup_statistics()
            logger.info(f"📊 백업 통계:")
            logger.info(f"  - 총 백업 수: {stats['total_backups']}")
            logger.info(f"  - 총 크기: {stats['total_size_mb']} MB")
            logger.info(f"  - 보관 기간: {stats['retention_days']}일")
            
            return True
        else:
            logger.error("백업 생성 실패")
            return False
            
    except Exception as e:
        log_error(logger, e, "백업 생성")
        return False

def check_system_status(enhanced_system: Dict[str, Any], logger):
    """시스템 상태 확인"""
    logger.info("🔍 시스템 상태 확인 중...")
    
    monitor = enhanced_system['monitor']
    backup_manager = enhanced_system['backup_manager']
    optimized_collector = enhanced_system['optimized_collector']
    security_manager = enhanced_system['security_manager']
    
    # 모니터링 상태
    system_status = monitor.get_system_status()
    logger.info("📊 시스템 상태:")
    logger.info(f"  - 활성 세션: {system_status.get('active_sessions', 0)}")
    logger.info(f"  - 잠긴 계정: {system_status.get('locked_accounts', 0)}")
    logger.info(f"  - 최근 이벤트: {system_status.get('recent_events_count', 0)}")
    logger.info(f"  - 실패한 로그인 (24h): {system_status.get('failed_logins_24h', 0)}")
    
    # 백업 상태
    backup_stats = backup_manager.get_backup_statistics()
    logger.info("💾 백업 상태:")
    logger.info(f"  - 총 백업 수: {backup_stats.get('total_backups', 0)}")
    logger.info(f"  - 총 크기: {backup_stats.get('total_size_mb', 0)} MB")
    logger.info(f"  - 최신 백업: {backup_stats.get('newest_backup', '없음')}")
    
    # 성능 통계
    perf_stats = optimized_collector.get_performance_stats()
    cache_stats = perf_stats['cache_stats']
    logger.info("⚡ 성능 상태:")
    logger.info(f"  - 캐시 히트율: {cache_stats.get('hit_rate', 0)}%")
    logger.info(f"  - 캐시 엔트리: {cache_stats.get('total_entries', 0)}")
    logger.info(f"  - 캐시 크기: {cache_stats.get('total_size_mb', 0)} MB")
    
    # 보안 상태
    security_report = security_manager.get_security_report()
    logger.info("🔒 보안 상태:")
    logger.info(f"  - 활성 세션: {security_report.get('active_sessions', 0)}")
    logger.info(f"  - 잠긴 계정: {security_report.get('locked_accounts', 0)}")
    logger.info(f"  - 보안 레벨: {security_report.get('security_level', 'UNKNOWN')}")

async def main():
    """메인 함수"""
    args = parse_arguments()
    
    # 로거 설정
    logger = setup_logger('dispersion_signal_enhanced', Config.LOG_FILE, Config.LOG_LEVEL)
    
    logger.info("=" * 80)
    logger.info("Dispersion Signal - 통합 개선된 데이터 수집 시스템")
    logger.info("=" * 80)
    
    try:
        # 개선된 시스템 초기화
        enhanced_system = initialize_enhanced_system(logger)
        
        # Supabase 클라이언트 초기화
        supabase_client = SupabaseClientPhase4(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        
        # 연결 테스트
        if args.test_connection:
            logger.info("🔗 연결 테스트 중...")
            if supabase_client.test_connection():
                logger.info("✅ Supabase 연결 성공")
            else:
                logger.error("❌ Supabase 연결 실패")
            return
        
        # 시스템 상태 확인
        if args.monitor_status:
            check_system_status(enhanced_system, logger)
            return
        
        # 백업 실행
        if args.backup:
            create_backup(enhanced_system, args.backup_type, logger)
            return
        
        # 활성 코인 목록 조회
        try:
            response = supabase_client.client.table('cryptocurrencies')\
                .select('id, symbol, name')\
                .eq('is_active', True)\
                .execute()
            cryptos = response.data
        except Exception as e:
            logger.error(f"활성 코인 목록 조회 실패: {e}")
            cryptos = []
        if not cryptos:
            logger.warning("활성 암호화폐를 찾을 수 없습니다.")
            return
        
        target_cryptos = cryptos[:args.coins]
        symbols = [crypto['symbol'] for crypto in target_cryptos]
        
        logger.info(f"분석 대상 코인: {symbols}")
        
        success_count = 0
        
        # 데이터 수집 실행
        if args.mode in ['prices', 'all']:
            if await collect_multi_source_prices_enhanced(symbols, supabase_client, enhanced_system, args.dry_run, logger):
                success_count += 1
        
        if args.mode in ['sentiment', 'all']:
            if await analyze_reddit_sentiment_enhanced(symbols, supabase_client, enhanced_system, args.dry_run, logger):
                success_count += 1
        
        # 자동 백업
        if args.enable_backup and not args.dry_run:
            create_backup(enhanced_system, 'incremental', logger)
        
        # 결과 출력
        if success_count > 0:
            logger.info(f"\n🎉 통합 시스템 작업 완료! ({success_count}개 작업 성공)")
            
            # 최종 상태 확인
            check_system_status(enhanced_system, logger)
            
        else:
            logger.error("\n💥 모든 작업 실패!")
            
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
    except Exception as e:
        log_error(logger, e, "메인 프로세스")

if __name__ == "__main__":
    asyncio.run(main())
