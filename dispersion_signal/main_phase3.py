#!/usr/bin/env python3
"""
Dispersion Signal - Phase 3 분산도 계산 및 신호 생성
"""
import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime, timezone, date, timedelta
from typing import List, Dict, Any
from uuid import UUID
from decimal import Decimal

# 프로젝트 모듈 임포트
from config import Config
from analysis.dispersion_calculator import DispersionCalculator
from database.supabase_client_phase3 import SupabaseClientPhase3
from database.models_phase3 import DispersionSignal, DispersionSummaryDaily
from utils.logger import setup_logger, log_error

def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='Phase 3: 분산도 계산 및 신호 생성',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python main_phase3.py --calculate --coins 20
  python main_phase3.py --summarize --date today
  python main_phase3.py --signals --level high
  python main_phase3.py --signals --type divergence
  python main_phase3.py --test-connection
        """
    )
    
    parser.add_argument(
        '--calculate',
        action='store_true',
        help='분산도 계산 실행'
    )
    
    parser.add_argument(
        '--summarize',
        action='store_true',
        help='일일 요약 생성'
    )
    
    parser.add_argument(
        '--signals',
        action='store_true',
        help='신호 조회'
    )
    
    parser.add_argument(
        '--coins', 
        type=int, 
        default=20,
        help='분석할 코인 수 (기본값: 20)'
    )
    
    parser.add_argument(
        '--date',
        type=str,
        default='today',
        help='요약 날짜 (today, yesterday, YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--level',
        type=str,
        choices=['low', 'medium', 'high'],
        help='신호 레벨 필터 (low: 1-2, medium: 3, high: 4-5)'
    )
    
    parser.add_argument(
        '--type',
        type=str,
        choices=['convergence', 'divergence', 'neutral'],
        help='신호 타입 필터'
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

def test_connection(supabase_client: SupabaseClientPhase3, logger):
    """연결 테스트"""
    logger.info("Phase 3 API 연결 테스트 중...")
    
    if supabase_client.test_connection():
        logger.info("✅ Supabase 연결 성공")
        
        # 데이터 요약 정보 출력
        summary = supabase_client.get_data_summary()
        if summary:
            logger.info("📊 데이터베이스 요약:")
            logger.info(f"  - 총 코인 수: {summary.get('total_coins', 0)}")
            logger.info(f"  - 분산도 신호: {summary.get('total_dispersion_signals', 0)}개 레코드")
            logger.info(f"  - 일일 요약: {summary.get('total_dispersion_summaries', 0)}개 레코드")
            logger.info(f"  - 시가총액 데이터: {summary.get('total_marketcap_records', 0)}개 레코드")
            logger.info(f"  - 글로벌 메트릭: {summary.get('total_global_records', 0)}개 레코드")
        
        return True
    else:
        logger.error("❌ Supabase 연결 실패")
        return False

def calculate_dispersion_signals(supabase_client: SupabaseClientPhase3,
                               calculator: DispersionCalculator,
                               symbols: List[str], dry_run: bool, logger) -> bool:
    """
    분산도 신호 계산
    
    Args:
        supabase_client: Supabase 클라이언트
        calculator: 분산도 계산기
        symbols: 코인 심볼 리스트
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info(f"분산도 신호 계산 시작: {len(symbols)}개 코인")
        
        signals = []
        timestamp = datetime.now(timezone.utc)
        
        # 글로벌 메트릭 조회
        global_metrics = supabase_client.get_latest_global_metrics()
        btc_dominance = Decimal(str(global_metrics.get('btc_dominance', 0))) if global_metrics else Decimal(0)
        eth_dominance = Decimal(str(global_metrics.get('eth_dominance', 0))) if global_metrics else Decimal(0)
        
        for symbol in symbols:
            try:
                # crypto_id 조회
                crypto_id = supabase_client.get_crypto_id(symbol)
                if not crypto_id:
                    logger.warning(f"crypto_id를 찾을 수 없습니다: {symbol}")
                    continue
                
                # 데이터 수집
                market_data = supabase_client.get_latest_market_data(crypto_id)
                market_cap_data = supabase_client.get_latest_market_cap_data(crypto_id)
                
                if not market_data and not market_cap_data:
                    logger.warning(f"시장 데이터를 찾을 수 없습니다: {symbol}")
                    continue
                
                # 가격 데이터 수집
                prices = []
                volumes = {}
                data_sources = []
                
                # Binance 데이터
                if market_data:
                    binance_price = Decimal(str(market_data.get('close_price', 0)))
                    binance_volume = Decimal(str(market_data.get('quote_volume', 0)))
                    if binance_price > 0:
                        prices.append(binance_price)
                        volumes['binance'] = binance_volume
                        data_sources.append('binance')
                
                # CoinMarketCap 데이터
                if market_cap_data:
                    cmc_price = Decimal(str(market_cap_data.get('market_cap', 0))) / Decimal(str(market_cap_data.get('circulating_supply', 1)))
                    if cmc_price > 0:
                        prices.append(cmc_price)
                        data_sources.append('coinmarketcap')
                
                if len(prices) < 1:
                    logger.warning(f"유효한 가격 데이터가 없습니다: {symbol}")
                    continue
                
                # 분산도 계산
                price_dispersion = calculator.calculate_price_dispersion(prices)
                volume_concentration = calculator.calculate_volume_concentration(volumes)
                
                # 신호 레벨 및 타입 계산
                signal_level, signal_type = calculator.calculate_signal_level(
                    price_dispersion, volume_concentration, Decimal(0)  # 도미넌스 변화는 단순화
                )
                
                # DispersionSignal 모델 생성
                signal = DispersionSignal(
                    crypto_id=crypto_id,
                    timestamp=timestamp,
                    price_dispersion=price_dispersion,
                    price_sources=len(prices),
                    price_max=max(prices) if prices else None,
                    price_min=min(prices) if prices else None,
                    price_avg=sum(prices) / len(prices) if prices else None,
                    volume_concentration=volume_concentration,
                    volume_total=sum(volumes.values()) if volumes else None,
                    btc_dominance=btc_dominance,
                    btc_dominance_change_7d=Decimal(0),  # 단순화
                    eth_dominance=eth_dominance,
                    eth_dominance_change_7d=Decimal(0),  # 단순화
                    signal_level=signal_level,
                    signal_type=signal_type,
                    data_sources=data_sources,
                    calculation_method='price_volume_dispersion',
                    raw_data={
                        'symbol': symbol,
                        'prices': [float(p) for p in prices],
                        'volumes': {k: float(v) for k, v in volumes.items()},
                        'global_metrics': global_metrics
                    }
                )
                
                signals.append(signal)
                
                logger.info(f"  {symbol}: 분산도={price_dispersion:.2f}%, 신호레벨={signal_level}, 타입={signal_type}")
                
            except Exception as e:
                log_error(logger, e, f"분산도 계산 실패: {symbol}")
                continue
        
        logger.info(f"✅ 분산도 신호 {len(signals)}개 계산 완료")
        
        if dry_run:
            logger.info("DRY RUN 모드: 계산 완료, 저장하지 않음")
            logger.info("계산된 신호 샘플 (첫 3개):")
            for i, signal in enumerate(signals[:3]):
                logger.info(f"  {i+1}. 신호레벨={signal.signal_level}, 타입={signal.signal_type}, 분산도={signal.price_dispersion:.2f}%")
            return True
        
        # 데이터베이스에 저장
        if signals:
            if supabase_client.insert_dispersion_signals(signals):
                logger.info(f"✅ 분산도 신호 {len(signals)}개 저장 완료")
                return True
            else:
                logger.error("❌ 분산도 신호 저장 실패")
                return False
        
        return False
        
    except Exception as e:
        log_error(logger, e, "분산도 신호 계산 프로세스")
        return False

def generate_daily_summary(supabase_client: SupabaseClientPhase3,
                          calculator: DispersionCalculator,
                          target_date: date, dry_run: bool, logger) -> bool:
    """
    일일 분산도 요약 생성
    
    Args:
        supabase_client: Supabase 클라이언트
        calculator: 분산도 계산기
        target_date: 대상 날짜
        dry_run: 드라이 런 모드
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info(f"일일 분산도 요약 생성: {target_date}")
        
        # 해당 날짜의 분산도 신호 조회
        start_time = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_time = start_time + timedelta(days=1)
        
        # 모든 분산도 신호 조회 (해당 날짜)
        response = supabase_client.client.table('dispersion_signals')\
            .select('*, cryptocurrencies(symbol)')\
            .gte('timestamp', start_time.isoformat())\
            .lt('timestamp', end_time.isoformat())\
            .execute()
        
        signals_data = response.data
        
        if not signals_data:
            logger.warning(f"해당 날짜의 분산도 신호가 없습니다: {target_date}")
            return False
        
        # 요약 계산
        summary_stats = calculator.calculate_market_dispersion_summary(signals_data)
        
        # 상위/하위 분산도 코인
        top_dispersion_coins = calculator.get_top_dispersion_coins(signals_data, 5)
        low_dispersion_coins = calculator.get_low_dispersion_coins(signals_data, 5)
        
        # 도미넌스 평균 계산
        btc_dominances = [s.get('btc_dominance', 0) for s in signals_data if s.get('btc_dominance')]
        eth_dominances = [s.get('eth_dominance', 0) for s in signals_data if s.get('eth_dominance')]
        
        btc_dominance_avg = sum(btc_dominances) / len(btc_dominances) if btc_dominances else Decimal(0)
        eth_dominance_avg = sum(eth_dominances) / len(eth_dominances) if eth_dominances else Decimal(0)
        
        # DispersionSummaryDaily 모델 생성
        summary = DispersionSummaryDaily(
            date=target_date,
            market_dispersion_avg=summary_stats['market_dispersion_avg'],
            market_dispersion_max=summary_stats['market_dispersion_max'],
            market_dispersion_min=summary_stats['market_dispersion_min'],
            top_dispersion_coins=top_dispersion_coins,
            low_dispersion_coins=low_dispersion_coins,
            btc_dominance_avg=round(btc_dominance_avg, 4),
            eth_dominance_avg=round(eth_dominance_avg, 4),
            high_signal_count=summary_stats['high_signal_count'],
            low_signal_count=summary_stats['low_signal_count'],
            coins_analyzed=summary_stats['coins_analyzed'],
            raw_data={
                'signals_count': len(signals_data),
                'date': target_date.isoformat(),
                'calculation_timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
        
        logger.info("✅ 일일 분산도 요약 계산 완료")
        logger.info(f"  - 평균 분산도: {summary.market_dispersion_avg:.2f}%")
        logger.info(f"  - 최대 분산도: {summary.market_dispersion_max:.2f}%")
        logger.info(f"  - 최소 분산도: {summary.market_dispersion_min:.2f}%")
        logger.info(f"  - 높은 신호: {summary.high_signal_count}개")
        logger.info(f"  - 낮은 신호: {summary.low_signal_count}개")
        
        if dry_run:
            logger.info("DRY RUN 모드: 계산 완료, 저장하지 않음")
            return True
        
        # 데이터베이스에 저장
        if supabase_client.insert_dispersion_summary(summary):
            logger.info("✅ 일일 분산도 요약 저장 완료")
            return True
        else:
            logger.error("❌ 일일 분산도 요약 저장 실패")
            return False
        
    except Exception as e:
        log_error(logger, e, "일일 분산도 요약 생성 프로세스")
        return False

def query_signals(supabase_client: SupabaseClientPhase3,
                  level: str, signal_type: str, limit: int, logger) -> bool:
    """
    신호 조회
    
    Args:
        supabase_client: Supabase 클라이언트
        level: 신호 레벨 필터
        signal_type: 신호 타입 필터
        limit: 조회할 레코드 수
        logger: 로거
    
    Returns:
        성공 여부
    """
    try:
        logger.info("분산도 신호 조회 중...")
        
        signals = []
        
        if level:
            # 레벨별 조회
            level_map = {'low': [1, 2], 'medium': [3], 'high': [4, 5]}
            target_levels = level_map.get(level, [])
            
            for target_level in target_levels:
                level_signals = supabase_client.get_dispersion_signals_by_level(target_level, limit)
                signals.extend(level_signals)
        elif signal_type:
            # 타입별 조회
            signals = supabase_client.get_dispersion_signals_by_type(signal_type, limit)
        else:
            # 최신 신호 조회
            response = supabase_client.client.table('dispersion_signals')\
                .select('*, cryptocurrencies(symbol, name)')\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            signals = response.data
        
        if not signals:
            logger.info("조회된 신호가 없습니다")
            return True
        
        logger.info(f"✅ {len(signals)}개 신호 조회 완료")
        logger.info("신호 목록:")
        
        for i, signal in enumerate(signals[:10]):  # 최대 10개만 출력
            crypto_info = signal.get('cryptocurrencies', {})
            symbol = crypto_info.get('symbol', 'Unknown')
            name = crypto_info.get('name', 'Unknown')
            
            logger.info(f"  {i+1}. {symbol} ({name})")
            logger.info(f"     신호레벨: {signal.get('signal_level', 'N/A')}")
            logger.info(f"     신호타입: {signal.get('signal_type', 'N/A')}")
            logger.info(f"     분산도: {signal.get('price_dispersion', 0):.2f}%")
            logger.info(f"     시간: {signal.get('timestamp', 'N/A')}")
        
        return True
        
    except Exception as e:
        log_error(logger, e, "신호 조회 프로세스")
        return False

def main():
    """메인 함수"""
    args = parse_arguments()
    
    # 로거 설정
    logger = setup_logger('dispersion_signal_phase3', Config.LOG_FILE, Config.LOG_LEVEL)
    
    logger.info("=" * 60)
    logger.info("Dispersion Signal - Phase 3 분산도 계산 및 신호 생성")
    logger.info("=" * 60)
    
    try:
        # 설정 검증
        Config.validate()
        
        # 클라이언트 초기화
        supabase_client = SupabaseClientPhase3(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        calculator = DispersionCalculator()
        calculator.logger = logger
        
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
        
        if args.calculate:
            logger.info("\n📊 분산도 신호 계산 시작...")
            if calculate_dispersion_signals(supabase_client, calculator, symbols, args.dry_run, logger):
                success_count += 1
        
        if args.summarize:
            logger.info("\n📈 일일 요약 생성 시작...")
            
            # 날짜 파싱
            if args.date == 'today':
                target_date = date.today()
            elif args.date == 'yesterday':
                target_date = date.today() - timedelta(days=1)
            else:
                try:
                    target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
                except ValueError:
                    logger.error(f"잘못된 날짜 형식: {args.date}")
                    sys.exit(1)
            
            if generate_daily_summary(supabase_client, calculator, target_date, args.dry_run, logger):
                success_count += 1
        
        if args.signals:
            logger.info("\n🔍 신호 조회 시작...")
            if query_signals(supabase_client, args.level, args.type, args.limit, logger):
                success_count += 1
        
        # 결과 출력
        if success_count > 0:
            logger.info(f"\n🎉 Phase 3 작업 완료! ({success_count}개 작업 성공)")
            
            if not args.dry_run:
                # 최신 데이터 확인
                summary = supabase_client.get_data_summary()
                if summary:
                    logger.info("📊 최종 데이터베이스 상태:")
                    logger.info(f"  - 총 코인 수: {summary.get('total_coins', 0)}")
                    logger.info(f"  - 분산도 신호: {summary.get('total_dispersion_signals', 0)}개 레코드")
                    logger.info(f"  - 일일 요약: {summary.get('total_dispersion_summaries', 0)}개 레코드")
            
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
