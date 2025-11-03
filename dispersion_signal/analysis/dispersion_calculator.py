"""
분산도 계산 모듈
"""
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import statistics
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import log_error

class DispersionCalculator:
    """분산도 계산 클래스"""
    
    def __init__(self):
        """분산도 계산기 초기화"""
        self.logger = None
    
    def calculate_price_dispersion(self, prices: List[Decimal]) -> Decimal:
        """
        가격 분산도 계산
        
        Args:
            prices: 가격 리스트
        
        Returns:
            분산도 (%)
        """
        try:
            if len(prices) < 2:
                return Decimal(0)
            
            # None 값 제거
            valid_prices = [p for p in prices if p is not None]
            if len(valid_prices) < 2:
                return Decimal(0)
            
            max_price = max(valid_prices)
            min_price = min(valid_prices)
            avg_price = sum(valid_prices) / len(valid_prices)
            
            if avg_price == 0:
                return Decimal(0)
            
            dispersion = (max_price - min_price) / avg_price * 100
            return round(dispersion, 4)
            
        except Exception as e:
            if self.logger:
                log_error(self.logger, e, "가격 분산도 계산 실패")
            return Decimal(0)
    
    def calculate_volume_concentration(self, volumes: Dict[str, Decimal]) -> Decimal:
        """
        거래량 집중도 계산 (HHI - Herfindahl-Hirschman Index)
        
        Args:
            volumes: 거래소별 거래량 딕셔너리
        
        Returns:
            HHI 점수 (0-10000)
        """
        try:
            if not volumes:
                return Decimal(0)
            
            # None 값 제거
            valid_volumes = {k: v for k, v in volumes.items() if v is not None and v > 0}
            if not valid_volumes:
                return Decimal(0)
            
            total_volume = sum(valid_volumes.values())
            if total_volume == 0:
                return Decimal(0)
            
            # HHI 계산: 각 거래소의 시장 점유율의 제곱의 합
            hhi = sum((v / total_volume) ** 2 for v in valid_volumes.values())
            return round(hhi * 10000, 4)  # 0-10000 범위
            
        except Exception as e:
            if self.logger:
                log_error(self.logger, e, "거래량 집중도 계산 실패")
            return Decimal(0)
    
    def calculate_dominance_trend(self, 
                                  historical_data: List[Dict[str, Any]],
                                  window: int = 7) -> Dict[str, Any]:
        """
        도미넌스 추세 계산
        
        Args:
            historical_data: 히스토리컬 도미넌스 데이터
            window: 이동 평균 윈도우 크기
        
        Returns:
            도미넌스 추세 정보
        """
        try:
            if len(historical_data) < window:
                return {
                    'btc_dominance_change_7d': Decimal(0),
                    'eth_dominance_change_7d': Decimal(0),
                    'trend_direction': 'insufficient_data'
                }
            
            # 최신 데이터와 과거 데이터 비교
            latest = historical_data[0]
            past = historical_data[min(window, len(historical_data) - 1)]
            
            btc_change = Decimal(0)
            eth_change = Decimal(0)
            
            if latest.get('btc_dominance') and past.get('btc_dominance'):
                btc_change = latest['btc_dominance'] - past['btc_dominance']
            
            if latest.get('eth_dominance') and past.get('eth_dominance'):
                eth_change = latest['eth_dominance'] - past['eth_dominance']
            
            # 추세 방향 결정
            trend_direction = 'neutral'
            if btc_change > Decimal(1):
                trend_direction = 'btc_increasing'
            elif btc_change < Decimal(-1):
                trend_direction = 'btc_decreasing'
            elif eth_change > Decimal(1):
                trend_direction = 'eth_increasing'
            elif eth_change < Decimal(-1):
                trend_direction = 'eth_decreasing'
            
            return {
                'btc_dominance_change_7d': round(btc_change, 4),
                'eth_dominance_change_7d': round(eth_change, 4),
                'trend_direction': trend_direction
            }
            
        except Exception as e:
            if self.logger:
                log_error(self.logger, e, "도미넌스 추세 계산 실패")
            return {
                'btc_dominance_change_7d': Decimal(0),
                'eth_dominance_change_7d': Decimal(0),
                'trend_direction': 'error'
            }
    
    def calculate_signal_level(self, 
                              price_dispersion: Decimal,
                              volume_concentration: Decimal,
                              dominance_change: Decimal) -> Tuple[int, str]:
        """
        신호 레벨 및 타입 계산
        
        Args:
            price_dispersion: 가격 분산도
            volume_concentration: 거래량 집중도
            dominance_change: 도미넌스 변화
        
        Returns:
            (신호 레벨, 신호 타입)
        """
        try:
            # 신호 레벨 계산 (1-5)
            signal_level = 1
            
            # 가격 분산도 기반 점수
            if price_dispersion > Decimal(5):
                signal_level += 2
            elif price_dispersion > Decimal(2):
                signal_level += 1
            
            # 거래량 집중도 기반 점수 (HHI > 2500이면 높은 집중도)
            if volume_concentration > Decimal(2500):
                signal_level += 1
            
            # 도미넌스 변화 기반 점수
            if abs(dominance_change) > Decimal(2):
                signal_level += 1
            
            # 신호 타입 결정
            signal_type = 'neutral'
            
            if price_dispersion > Decimal(3) and volume_concentration > Decimal(2000):
                signal_type = 'divergence'  # 높은 분산도 + 높은 집중도
            elif price_dispersion < Decimal(1) and volume_concentration < Decimal(1500):
                signal_type = 'convergence'  # 낮은 분산도 + 낮은 집중도
            
            return min(signal_level, 5), signal_type
            
        except Exception as e:
            if self.logger:
                log_error(self.logger, e, "신호 레벨 계산 실패")
            return 1, 'neutral'
    
    def calculate_market_dispersion_summary(self, 
                                           dispersion_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        전체 시장 분산도 요약 계산
        
        Args:
            dispersion_data: 모든 코인의 분산도 데이터
        
        Returns:
            시장 요약 정보
        """
        try:
            if not dispersion_data:
                return {
                    'market_dispersion_avg': Decimal(0),
                    'market_dispersion_max': Decimal(0),
                    'market_dispersion_min': Decimal(0),
                    'high_signal_count': 0,
                    'low_signal_count': 0,
                    'coins_analyzed': 0
                }
            
            # 분산도 값들 추출
            dispersions = [d.get('price_dispersion', Decimal(0)) for d in dispersion_data 
                          if d.get('price_dispersion') is not None]
            
            signal_levels = [d.get('signal_level', 1) for d in dispersion_data 
                           if d.get('signal_level') is not None]
            
            if not dispersions:
                return {
                    'market_dispersion_avg': Decimal(0),
                    'market_dispersion_max': Decimal(0),
                    'market_dispersion_min': Decimal(0),
                    'high_signal_count': 0,
                    'low_signal_count': 0,
                    'coins_analyzed': len(dispersion_data)
                }
            
            # 통계 계산
            avg_dispersion = sum(dispersions) / len(dispersions)
            max_dispersion = max(dispersions)
            min_dispersion = min(dispersions)
            
            # 신호 통계
            high_signals = sum(1 for level in signal_levels if level >= 4)
            low_signals = sum(1 for level in signal_levels if level <= 2)
            
            return {
                'market_dispersion_avg': round(avg_dispersion, 4),
                'market_dispersion_max': round(max_dispersion, 4),
                'market_dispersion_min': round(min_dispersion, 4),
                'high_signal_count': high_signals,
                'low_signal_count': low_signals,
                'coins_analyzed': len(dispersion_data)
            }
            
        except Exception as e:
            if self.logger:
                log_error(self.logger, e, "시장 분산도 요약 계산 실패")
            return {
                'market_dispersion_avg': Decimal(0),
                'market_dispersion_max': Decimal(0),
                'market_dispersion_min': Decimal(0),
                'high_signal_count': 0,
                'low_signal_count': 0,
                'coins_analyzed': 0
            }
    
    def get_top_dispersion_coins(self, 
                                 dispersion_data: List[Dict[str, Any]], 
                                 top_n: int = 5) -> List[str]:
        """
        분산도가 높은 상위 코인 조회
        
        Args:
            dispersion_data: 분산도 데이터
            top_n: 상위 N개
        
        Returns:
            코인 심볼 리스트
        """
        try:
            # 분산도 기준으로 정렬
            sorted_data = sorted(dispersion_data, 
                               key=lambda x: x.get('price_dispersion', Decimal(0)), 
                               reverse=True)
            
            return [d.get('symbol', '') for d in sorted_data[:top_n] 
                   if d.get('symbol')]
            
        except Exception as e:
            if self.logger:
                log_error(self.logger, e, "상위 분산도 코인 조회 실패")
            return []
    
    def get_low_dispersion_coins(self, 
                                 dispersion_data: List[Dict[str, Any]], 
                                 top_n: int = 5) -> List[str]:
        """
        분산도가 낮은 상위 코인 조회
        
        Args:
            dispersion_data: 분산도 데이터
            top_n: 상위 N개
        
        Returns:
            코인 심볼 리스트
        """
        try:
            # 분산도 기준으로 정렬 (낮은 순)
            sorted_data = sorted(dispersion_data, 
                               key=lambda x: x.get('price_dispersion', Decimal(0)))
            
            return [d.get('symbol', '') for d in sorted_data[:top_n] 
                   if d.get('symbol')]
            
        except Exception as e:
            if self.logger:
                log_error(self.logger, e, "하위 분산도 코인 조회 실패")
            return []
