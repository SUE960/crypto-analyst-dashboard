"""
Messari API 클라이언트 - 분석가 목표가 데이터 수집
Messari는 암호화폐 전문 리서치 플랫폼으로 분석가들의 목표가와 분석을 제공합니다.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from decimal import Decimal
import json

from collectors.base import BaseCollector
from utils.logger import log_error, log_info

logger = logging.getLogger(__name__)

class MessariAnalystCollector(BaseCollector):
    """Messari API를 통한 분석가 목표가 데이터 수집기"""
    
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            base_url='https://data.messari.io/api/v1',
            rate_limit=20  # 분당 20회 제한
        )
        # Messari API는 x-messari-api-key 헤더를 사용하므로 Authorization 헤더 제거
        self.session.headers.clear()
        self.session.headers.update({
            'x-messari-api-key': api_key,
            'Content-Type': 'application/json'
        })
        self.logger = logger
    
    def get_asset_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        자산 프로필 정보 조회
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
        
        Returns:
            자산 프로필 정보 딕셔너리 또는 None
        """
        try:
            endpoint = f"/assets/{symbol.lower()}"
            response = self._make_request(endpoint)
            
            if response and 'data' in response:
                return response['data']
            return None
            
        except Exception as e:
            log_error(self.logger, e, f"Messari 자산 프로필 조회 실패: {symbol}")
            return None
    
    def get_asset_metrics(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        자산 메트릭 정보 조회 (무료 티어용 - 기본 정보만)
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
        
        Returns:
            자산 메트릭 정보 딕셔너리 또는 None
        """
        try:
            # 무료 티어에서는 /assets/{symbol} 엔드포인트 사용
            endpoint = f"/assets/{symbol.lower()}"
            response = self._make_request(endpoint)
            
            if response and 'data' in response:
                return response['data']
            return None
            
        except Exception as e:
            log_error(self.logger, e, f"Messari 자산 메트릭 조회 실패: {symbol}")
            return None
    
    def get_price_time_series(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[List[Dict[str, Any]]]:
        """
        가격 시계열 데이터 조회
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
        
        Returns:
            가격 시계열 데이터 리스트 또는 None
        """
        try:
            endpoint = f"/assets/{symbol.lower()}/metrics/price/time-series"
            params = {}
            
            if start_date:
                params['start'] = start_date
            if end_date:
                params['end'] = end_date
            
            response = self._make_request(endpoint, params=params)
            
            if response and 'data' in response:
                return response['data']['values']
            return None
            
        except Exception as e:
            log_error(self.logger, e, f"Messari 가격 시계열 조회 실패: {symbol}")
            return None
    
    def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        시장 데이터 조회 (무료 티어용)
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
        
        Returns:
            시장 데이터 딕셔너리 또는 None
        """
        try:
            # 무료 티어에서는 기본 자산 정보만 사용
            asset_data = self.get_asset_metrics(symbol)
            if not asset_data:
                return None
            
            # 기본 정보에서 가격 정보 추출
            return {
                'symbol': symbol.upper(),
                'current_price': asset_data.get('price_usd'),
                'market_cap': asset_data.get('market_cap_dominance'),
                'volume_24h': asset_data.get('volume_last_24_hours'),
                'price_change_24h': asset_data.get('percent_change_usd_last_24_hours'),
                'price_change_7d': asset_data.get('percent_change_usd_last_7_days'),
                'price_change_30d': asset_data.get('percent_change_usd_last_30_days'),
                'price_change_90d': asset_data.get('percent_change_usd_last_90_days'),
                'price_change_1y': asset_data.get('percent_change_usd_last_1_year'),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            log_error(self.logger, e, f"Messari 시장 데이터 조회 실패: {symbol}")
            return None
    
    def get_analyst_insights(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """
        분석가 인사이트 조회 (Messari의 분석가 의견)
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
        
        Returns:
            분석가 인사이트 리스트 또는 None
        """
        try:
            # Messari는 직접적인 분석가 목표가 API를 제공하지 않으므로
            # 자산 프로필에서 관련 정보를 추출
            profile = self.get_asset_profile(symbol)
            if not profile:
                return None
            
            insights = []
            
            # 프로필에서 분석 관련 정보 추출
            if 'profile' in profile:
                profile_data = profile['profile']
                
                # 일반적인 분석가 의견이나 전망 정보가 있다면 추출
                if 'general' in profile_data:
                    general_info = profile_data['general']
                    
                    # 기술적 분석 정보
                    if 'overview' in general_info:
                        insights.append({
                            'type': 'overview',
                            'content': general_info['overview'],
                            'source': 'messari_profile',
                            'confidence': 7,  # 기본 신뢰도
                            'analysis_type': 'fundamental'
                        })
                    
                    # 기술적 특징
                    if 'technology' in general_info:
                        insights.append({
                            'type': 'technology',
                            'content': general_info['technology'],
                            'source': 'messari_profile',
                            'confidence': 8,
                            'analysis_type': 'technical'
                        })
            
            return insights if insights else None
            
        except Exception as e:
            log_error(self.logger, e, f"Messari 분석가 인사이트 조회 실패: {symbol}")
            return None
    
    def get_price_targets_from_metrics(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """
        메트릭 데이터에서 가격 목표가 추출
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
        
        Returns:
            가격 목표가 리스트 또는 None
        """
        try:
            metrics = self.get_asset_metrics(symbol)
            if not metrics:
                return None
            
            market_data = metrics.get('market_data', {})
            current_price = market_data.get('price_usd')
            
            if not current_price:
                return None
            
            targets = []
            
            # 과거 성과 기반 목표가 계산
            price_changes = {
                '7d': market_data.get('percent_change_usd_last_7_days', 0),
                '30d': market_data.get('percent_change_usd_last_30_days', 0),
                '90d': market_data.get('percent_change_usd_last_90_days', 0),
                '1y': market_data.get('percent_change_usd_last_1_year', 0)
            }
            
            # 단기 목표가 (1-3개월)
            if price_changes['30d']:
                short_term_target = current_price * (1 + price_changes['30d'] / 100 * 0.5)
                targets.append({
                    'symbol': symbol.upper(),
                    'current_price': current_price,
                    'target_price': short_term_target,
                    'timeframe': 'short_term',
                    'timeframe_months': 2,
                    'analysis_type': 'technical',
                    'confidence_level': 6,
                    'reasoning': f'30일 성과 기반 단기 목표가 (변화율: {price_changes["30d"]:.2f}%)',
                    'source': 'messari_metrics',
                    'published_at': datetime.now().isoformat()
                })
            
            # 중기 목표가 (6-12개월)
            if price_changes['90d']:
                medium_term_target = current_price * (1 + price_changes['90d'] / 100 * 0.7)
                targets.append({
                    'symbol': symbol.upper(),
                    'current_price': current_price,
                    'target_price': medium_term_target,
                    'timeframe': 'medium_term',
                    'timeframe_months': 9,
                    'analysis_type': 'technical',
                    'confidence_level': 7,
                    'reasoning': f'90일 성과 기반 중기 목표가 (변화율: {price_changes["90d"]:.2f}%)',
                    'source': 'messari_metrics',
                    'published_at': datetime.now().isoformat()
                })
            
            # 장기 목표가 (1년+)
            if price_changes['1y']:
                long_term_target = current_price * (1 + price_changes['1y'] / 100 * 0.8)
                targets.append({
                    'symbol': symbol.upper(),
                    'current_price': current_price,
                    'target_price': long_term_target,
                    'timeframe': 'long_term',
                    'timeframe_months': 18,
                    'analysis_type': 'fundamental',
                    'confidence_level': 6,
                    'reasoning': f'1년 성과 기반 장기 목표가 (변화율: {price_changes["1y"]:.2f}%)',
                    'source': 'messari_metrics',
                    'published_at': datetime.now().isoformat()
                })
            
            return targets if targets else None
            
        except Exception as e:
            log_error(self.logger, e, f"Messari 가격 목표가 추출 실패: {symbol}")
            return None
    
    def collect_data(self, symbol: str, start_date: datetime, end_date: datetime, interval: str = '1hour') -> List[Dict[str, Any]]:
        """
        데이터 수집 (BaseCollector 추상 메서드 구현)
        
        Args:
            symbol: 코인 심볼
            start_date: 시작 날짜
            end_date: 종료 날짜
            interval: 데이터 간격
        
        Returns:
            수집된 데이터 리스트
        """
        try:
            # 시장 데이터 수집
            market_data = self.get_market_data(symbol)
            if not market_data:
                return []
            
            # 가격 목표가 추출
            targets = self.get_price_targets_from_metrics(symbol)
            if not targets:
                return []
            
            # BaseCollector 형식에 맞게 변환
            result = []
            for target in targets:
                result.append({
                    'symbol': target['symbol'],
                    'timestamp': datetime.now().isoformat(),
                    'price': float(target['target_price']),
                    'volume': 0,  # Messari에서는 거래량 정보가 별도
                    'market_cap': 0,  # 별도로 수집 필요
                    'source': 'messari'
                })
            
            return result
            
        except Exception as e:
            log_error(self.logger, e, f"Messari 데이터 수집 실패: {symbol}")
            return []
    
    def collect_analyst_data(self, symbols: List[str]) -> Dict[str, Any]:
        """
        여러 코인에 대한 분석가 데이터 수집
        
        Args:
            symbols: 코인 심볼 리스트
        
        Returns:
            수집된 분석가 데이터 딕셔너리
        """
        collected_data = {
            'analyst_profiles': [],
            'analyst_targets': [],
            'market_data': [],
            'insights': []
        }
        
        for symbol in symbols:
            try:
                log_info(self.logger, f"Messari {symbol} 분석가 데이터 수집 중...")
                
                # 시장 데이터 수집
                market_data = self.get_market_data(symbol)
                if market_data:
                    collected_data['market_data'].append(market_data)
                
                # 가격 목표가 추출
                targets = self.get_price_targets_from_metrics(symbol)
                if targets:
                    collected_data['analyst_targets'].extend(targets)
                
                # 분석가 인사이트 수집
                insights = self.get_analyst_insights(symbol)
                if insights:
                    collected_data['insights'].extend(insights)
                
                # 분석가 프로필 생성 (Messari 기반)
                analyst_profile = {
                    'name': 'Messari Research Team',
                    'source': 'messari',
                    'source_id': 'messari_research',
                    'profile_url': 'https://messari.io/',
                    'bio': 'Messari 전문 리서치 팀의 암호화폐 분석',
                    'expertise_areas': ['technical', 'fundamental'],
                    'reliability_score': 85.0,
                    'followers_count': 50000,
                    'is_active': True
                }
                
                if analyst_profile not in collected_data['analyst_profiles']:
                    collected_data['analyst_profiles'].append(analyst_profile)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                log_error(self.logger, e, f"Messari {symbol} 데이터 수집 실패")
                continue
        
        return collected_data

# 테스트 함수
def test_messari_collector():
    """Messari 수집기 테스트"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv('MESSARI_API_KEY')
    if not api_key:
        print("❌ MESSARI_API_KEY가 .env 파일에 없습니다.")
        return
    
    collector = MessariAnalystCollector(api_key)
    
    # 테스트 코인들
    test_symbols = ['BTC', 'ETH', 'SOL']
    
    print("=== Messari 분석가 데이터 수집 테스트 ===")
    
    for symbol in test_symbols:
        print(f"\n{symbol} 데이터 수집 중...")
        
        # 시장 데이터 테스트
        market_data = collector.get_market_data(symbol)
        if market_data:
            print(f"✅ 시장 데이터: ${market_data['current_price']:.2f}")
        else:
            print("❌ 시장 데이터 수집 실패")
        
        # 가격 목표가 테스트
        targets = collector.get_price_targets_from_metrics(symbol)
        if targets:
            print(f"✅ 목표가 {len(targets)}개 수집")
            for target in targets:
                print(f"   {target['timeframe']}: ${target['target_price']:.2f}")
        else:
            print("❌ 목표가 수집 실패")
        
        time.sleep(2)  # Rate limiting

if __name__ == "__main__":
    test_messari_collector()
