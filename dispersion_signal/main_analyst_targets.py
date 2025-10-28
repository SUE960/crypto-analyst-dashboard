"""
분석가 목표가 데이터 통합 수집 스크립트
여러 소스에서 분석가 목표가 데이터를 수집하고 Supabase에 저장
"""

import asyncio
import argparse
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import os
from dotenv import load_dotenv

# 로컬 모듈 임포트
from config import Config
from utils.logger import setup_logger, log_info, log_error
from database.supabase_client_analyst_targets import SupabaseClientAnalystTargets
from database.models_analyst_targets import (
    CollectedAnalystData, AnalystProfile, AnalystTarget, 
    MarketInsight, SentimentAnalysis, MarketIndex, SectorAnalysis
)

# 수집기 임포트
from collectors.messari_analyst import MessariAnalystCollector
from collectors.digitalcoinprice import DigitalCoinPriceCollector
from collectors.coinpriceforecast import CoinPriceForecastCollector
from collectors.coinness import CoinnessNewsCollector
from collectors.upbit_datalab import UpbitDataLabCollector

# 로깅 설정
logger = setup_logger('analyst_targets_collector')

class AnalystTargetsCollector:
    """분석가 목표가 데이터 통합 수집기"""
    
    def __init__(self):
        """수집기 초기화"""
        self.supabase_client = SupabaseClientAnalystTargets(
            Config.SUPABASE_URL, 
            Config.SUPABASE_SERVICE_ROLE_KEY
        )
        
        # 수집기들 초기화
        self.collectors = {}
        
        # Messari 수집기 (API 키 필요)
        if Config.MESSARI_API_KEY:
            self.collectors['messari'] = MessariAnalystCollector(Config.MESSARI_API_KEY)
            log_info(logger, "Messari 수집기 초기화 완료")
        else:
            log_info(logger, "Messari API 키가 없어 수집기를 건너뜁니다")
        
        # 웹 스크래핑 수집기들
        self.collectors['digitalcoinprice'] = DigitalCoinPriceCollector()
        self.collectors['coinpriceforecast'] = CoinPriceForecastCollector()
        self.collectors['coinness'] = CoinnessNewsCollector()
        self.collectors['upbit_datalab'] = UpbitDataLabCollector()
        
        log_info(logger, f"총 {len(self.collectors)}개 수집기 초기화 완료")
    
    async def collect_from_messari(self, symbols: List[str]) -> Dict[str, Any]:
        """Messari에서 데이터 수집"""
        if 'messari' not in self.collectors:
            return {}
        
        try:
            log_info(logger, "Messari 데이터 수집 시작")
            data = self.collectors['messari'].collect_analyst_data(symbols)
            log_info(logger, f"Messari 데이터 수집 완료: {len(data.get('analyst_targets', []))}개 목표가")
            return data
        except Exception as e:
            log_error(logger, e, "Messari 데이터 수집 실패")
            return {}
    
    async def collect_from_digitalcoinprice(self, symbols: List[str]) -> Dict[str, Any]:
        """DigitalCoinPrice에서 데이터 수집"""
        try:
            log_info(logger, "DigitalCoinPrice 데이터 수집 시작")
            data = self.collectors['digitalcoinprice'].collect_analyst_data(symbols)
            log_info(logger, f"DigitalCoinPrice 데이터 수집 완료: {len(data.get('analyst_targets', []))}개 목표가")
            return data
        except Exception as e:
            log_error(logger, e, "DigitalCoinPrice 데이터 수집 실패")
            return {}
    
    async def collect_from_coinpriceforecast(self, symbols: List[str]) -> Dict[str, Any]:
        """CoinPriceForecast에서 데이터 수집"""
        try:
            log_info(logger, "CoinPriceForecast 데이터 수집 시작")
            data = self.collectors['coinpriceforecast'].collect_analyst_data(symbols)
            log_info(logger, f"CoinPriceForecast 데이터 수집 완료: {len(data.get('analyst_targets', []))}개 목표가")
            return data
        except Exception as e:
            log_error(logger, e, "CoinPriceForecast 데이터 수집 실패")
            return {}
    
    async def collect_from_coinness(self, symbols: List[str]) -> Dict[str, Any]:
        """Coinness에서 데이터 수집"""
        try:
            log_info(logger, "Coinness 데이터 수집 시작")
            data = self.collectors['coinness'].collect_analyst_data(symbols)
            log_info(logger, f"Coinness 데이터 수집 완료: {len(data.get('analyst_targets', []))}개 목표가")
            return data
        except Exception as e:
            log_error(logger, e, "Coinness 데이터 수집 실패")
            return {}
    
    async def collect_from_upbit_datalab(self) -> Dict[str, Any]:
        """Upbit DataLab에서 데이터 수집"""
        try:
            log_info(logger, "Upbit DataLab 데이터 수집 시작")
            data = self.collectors['upbit_datalab'].collect_analyst_data()
            log_info(logger, f"Upbit DataLab 데이터 수집 완료: {len(data.get('analyst_targets', []))}개 목표가")
            return data
        except Exception as e:
            log_error(logger, e, "Upbit DataLab 데이터 수집 실패")
            return {}
    
    def merge_collected_data(self, all_data: List[Dict[str, Any]]) -> CollectedAnalystData:
        """수집된 데이터 통합"""
        merged_data = CollectedAnalystData()
        
        for data in all_data:
            if not data:
                continue
            
            # 분석가 프로필 통합
            if 'analyst_profiles' in data:
                for profile_data in data['analyst_profiles']:
                    try:
                        profile = AnalystProfile(**profile_data)
                        merged_data.analyst_profiles.append(profile)
                    except Exception as e:
                        log_error(logger, e, f"분석가 프로필 파싱 실패: {profile_data}")
            
            # 분석가 목표가 통합
            if 'analyst_targets' in data:
                for target_data in data['analyst_targets']:
                    try:
                        target = AnalystTarget(**target_data)
                        merged_data.analyst_targets.append(target)
                    except Exception as e:
                        log_error(logger, e, f"분석가 목표가 파싱 실패: {target_data}")
            
            # 시장 인사이트 통합
            if 'insights' in data:
                for insight_data in data['insights']:
                    try:
                        insight = MarketInsight(**insight_data)
                        merged_data.market_insights.append(insight)
                    except Exception as e:
                        log_error(logger, e, f"시장 인사이트 파싱 실패: {insight_data}")
            
            # 감성 분석 통합
            if 'sentiment_analysis' in data:
                for sentiment_data in data['sentiment_analysis']:
                    try:
                        sentiment = SentimentAnalysis(**sentiment_data)
                        merged_data.sentiment_analysis.append(sentiment)
                    except Exception as e:
                        log_error(logger, e, f"감성 분석 파싱 실패: {sentiment_data}")
            
            # 시장 지수 통합
            if 'market_indices' in data:
                for index_data in data['market_indices']:
                    try:
                        index = MarketIndex(**index_data)
                        merged_data.market_indices.append(index)
                    except Exception as e:
                        log_error(logger, e, f"시장 지수 파싱 실패: {index_data}")
            
            # 섹터 분석 통합
            if 'sector_analysis' in data:
                for sector_data in data['sector_analysis']:
                    try:
                        sector = SectorAnalysis(**sector_data)
                        merged_data.sector_analysis.append(sector)
                    except Exception as e:
                        log_error(logger, e, f"섹터 분석 파싱 실패: {sector_data}")
        
        log_info(logger, f"데이터 통합 완료: 총 {merged_data.total_records}개 레코드")
        return merged_data
    
    async def collect_all_data(self, symbols: List[str], dry_run: bool = False) -> bool:
        """모든 소스에서 데이터 수집"""
        try:
            log_info(logger, f"분석가 목표가 데이터 수집 시작: {len(symbols)}개 코인")
            
            # 비동기 데이터 수집
            tasks = []
            
            # Messari (API 기반)
            if 'messari' in self.collectors:
                tasks.append(self.collect_from_messari(symbols))
            
            # 웹 스크래핑 (병렬 실행)
            tasks.append(self.collect_from_digitalcoinprice(symbols))
            tasks.append(self.collect_from_coinpriceforecast(symbols))
            tasks.append(self.collect_from_coinness(symbols))
            tasks.append(self.collect_from_upbit_datalab())
            
            # 모든 수집 작업 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 처리
            all_data = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    log_error(logger, result, f"수집 작업 {i} 실패")
                else:
                    all_data.append(result)
            
            # 데이터 통합
            merged_data = self.merge_collected_data(all_data)
            
            if dry_run:
                log_info(logger, f"Dry-run 모드: 데이터 저장 건너뜀")
                log_info(logger, f"수집된 데이터: {merged_data.total_records}개 레코드")
                return True
            
            # Supabase에 저장
            save_results = self.supabase_client.save_collected_data(merged_data)
            
            # 결과 요약
            total_saved = sum(save_results[key] for key in save_results if key != 'errors')
            log_info(logger, f"데이터 저장 완료: {total_saved}개 성공, {save_results['errors']}개 실패")
            
            return save_results['errors'] == 0
            
        except Exception as e:
            log_error(logger, e, "분석가 목표가 데이터 수집 실패")
            return False
    
    def get_collection_status(self) -> Dict[str, Any]:
        """수집 상태 조회"""
        try:
            # 최근 목표가 조회
            recent_targets = self.supabase_client.get_recent_targets(10)
            
            # 상위 분석가 조회
            top_analysts = self.supabase_client.get_top_analysts(5)
            
            # 코인별 집계 조회
            symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'BNB']
            coin_summaries = {}
            for symbol in symbols:
                summary = self.supabase_client.get_coin_analyst_summary(symbol)
                if summary:
                    coin_summaries[symbol] = summary
            
            return {
                'recent_targets_count': len(recent_targets),
                'top_analysts_count': len(top_analysts),
                'coin_summaries_count': len(coin_summaries),
                'last_updated': datetime.now().isoformat(),
                'status': 'healthy'
            }
            
        except Exception as e:
            log_error(logger, e, "수집 상태 조회 실패")
            return {
                'status': 'error',
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }

async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='분석가 목표가 데이터 수집기')
    parser.add_argument('--mode', choices=['collect', 'status', 'test'], 
                       default='collect', help='실행 모드')
    parser.add_argument('--symbols', nargs='+', 
                       default=['BTC', 'ETH', 'SOL', 'XRP', 'BNB', 'DOGE', 'TRX', 'SUI', 'AVAX', 'TAO'],
                       help='수집할 코인 심볼들')
    parser.add_argument('--dry-run', action='store_true', 
                       help='실제 저장 없이 테스트만 실행')
    parser.add_argument('--max-symbols', type=int, default=10,
                       help='최대 수집할 코인 수')
    
    args = parser.parse_args()
    
    # 환경 변수 로드
    load_dotenv()
    
    # 수집기 초기화
    collector = AnalystTargetsCollector()
    
    if args.mode == 'test':
        # 수집기 테스트 (데이터베이스 연결 없이)
        log_info(logger, "수집기 테스트 시작")
        test_symbols = args.symbols[:3]  # 처음 3개만 테스트
        
        # Messari 테스트
        if 'messari' in collector.collectors:
            try:
                messari_data = await collector.collect_from_messari(test_symbols)
                log_info(logger, f"✅ Messari 테스트 성공: {len(messari_data.get('analyst_targets', []))}개 목표가")
            except Exception as e:
                log_error(logger, e, "❌ Messari 테스트 실패")
        
        # 웹 스크래핑 테스트
        try:
            digitalcoinprice_data = await collector.collect_from_digitalcoinprice(test_symbols)
            log_info(logger, f"✅ DigitalCoinPrice 테스트 성공: {len(digitalcoinprice_data.get('analyst_targets', []))}개 목표가")
        except Exception as e:
            log_error(logger, e, "❌ DigitalCoinPrice 테스트 실패")
        
        try:
            coinpriceforecast_data = await collector.collect_from_coinpriceforecast(test_symbols)
            log_info(logger, f"✅ CoinPriceForecast 테스트 성공: {len(coinpriceforecast_data.get('analyst_targets', []))}개 목표가")
        except Exception as e:
            log_error(logger, e, "❌ CoinPriceForecast 테스트 실패")
        
        try:
            coinness_data = await collector.collect_from_coinness(test_symbols)
            log_info(logger, f"✅ Coinness 테스트 성공: {len(coinness_data.get('analyst_targets', []))}개 목표가")
        except Exception as e:
            log_error(logger, e, "❌ Coinness 테스트 실패")
        
        try:
            upbit_data = await collector.collect_from_upbit_datalab()
            log_info(logger, f"✅ Upbit DataLab 테스트 성공: {len(upbit_data.get('analyst_targets', []))}개 목표가")
        except Exception as e:
            log_error(logger, e, "❌ Upbit DataLab 테스트 실패")
        
        log_info(logger, "수집기 테스트 완료")
    
    elif args.mode == 'status':
        # 상태 조회
        log_info(logger, "수집 상태 조회 시작")
        status = collector.get_collection_status()
        
        log_info(logger, f"수집 상태: {status['status']}")
        log_info(logger, f"최근 목표가: {status.get('recent_targets_count', 0)}개")
        log_info(logger, f"상위 분석가: {status.get('top_analysts_count', 0)}개")
        log_info(logger, f"코인별 집계: {status.get('coin_summaries_count', 0)}개")
        
        if status['status'] == 'error':
            log_error(logger, None, f"상태 조회 오류: {status.get('error', 'Unknown error')}")
    
    elif args.mode == 'collect':
        # 데이터 수집
        symbols = args.symbols[:args.max_symbols]
        
        log_info(logger, f"분석가 목표가 데이터 수집 시작: {len(symbols)}개 코인")
        log_info(logger, f"수집 대상 코인: {', '.join(symbols)}")
        
        if args.dry_run:
            log_info(logger, "Dry-run 모드로 실행")
        
        success = await collector.collect_all_data(symbols, dry_run=args.dry_run)
        
        if success:
            log_info(logger, "✅ 분석가 목표가 데이터 수집 완료")
        else:
            log_error(logger, None, "❌ 분석가 목표가 데이터 수집 실패")

if __name__ == "__main__":
    asyncio.run(main())
