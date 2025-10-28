"""
CoinCap API 클라이언트
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collectors.base import BaseCollector
from utils.logger import log_error

class CoinCapCollector(BaseCollector):
    """CoinCap API 클라이언트"""
    
    def __init__(self):
        super().__init__(
            api_key=None,  # API 키 불필요
            base_url='https://api.coincap.io/v2',
            rate_limit=1000  # 제한 없음
        )
    
    def get_assets(self, limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        상위 코인 목록 조회
        
        Args:
            limit: 조회할 코인 수
        
        Returns:
            코인 목록 데이터
        """
        endpoint = "/assets"
        params = {'limit': limit}
        return self._make_request(endpoint, params=params)
    
    def get_asset_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        심볼로 코인 정보 조회
        
        Args:
            symbol: 코인 심볼 (예: 'bitcoin')
        
        Returns:
            코인 정보 데이터
        """
        endpoint = f"/assets/{symbol.lower()}"
        return self._make_request(endpoint)
    
    def get_asset_by_id(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        ID로 코인 정보 조회
        
        Args:
            asset_id: 코인 ID (예: 'bitcoin')
        
        Returns:
            코인 정보 데이터
        """
        endpoint = f"/assets/{asset_id}"
        return self._make_request(endpoint)
    
    def get_asset_history(self, asset_id: str, interval: str = 'd1', 
                         days: int = 30) -> Optional[Dict[str, Any]]:
        """
        코인별 히스토리컬 데이터
        
        Args:
            asset_id: 코인 ID
            interval: 간격 (m1, m5, m15, m30, h1, h2, h6, h12, d1)
            days: 조회할 일수
        
        Returns:
            히스토리컬 데이터
        """
        endpoint = f"/assets/{asset_id}/history"
        
        # 날짜 계산
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        
        params = {
            'interval': interval,
            'start': int(start_time.timestamp() * 1000),
            'end': int(end_time.timestamp() * 1000)
        }
        return self._make_request(endpoint, params=params)
    
    def get_rates(self) -> Optional[Dict[str, Any]]:
        """
        실시간 환율 정보
        
        Returns:
            환율 데이터
        """
        endpoint = "/rates"
        return self._make_request(endpoint)
    
    def get_exchanges(self) -> Optional[Dict[str, Any]]:
        """
        거래소 목록
        
        Returns:
            거래소 목록 데이터
        """
        endpoint = "/exchanges"
        return self._make_request(endpoint)
    
    def get_markets(self, exchange_id: str = None) -> Optional[Dict[str, Any]]:
        """
        시장 데이터 조회
        
        Args:
            exchange_id: 거래소 ID (선택사항)
        
        Returns:
            시장 데이터
        """
        endpoint = "/markets"
        params = {}
        if exchange_id:
            params['exchangeId'] = exchange_id
        return self._make_request(endpoint, params=params)
    
    def search_assets(self, search: str) -> Optional[Dict[str, Any]]:
        """
        코인 검색
        
        Args:
            search: 검색어
        
        Returns:
            검색 결과
        """
        endpoint = "/assets"
        params = {'search': search}
        return self._make_request(endpoint, params=params)
    
    def get_top_coins(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        상위 코인 목록 조회 (편의 메서드)
        
        Args:
            limit: 조회할 코인 수
        
        Returns:
            상위 코인 목록
        """
        try:
            response = self.get_assets(limit)
            if response and 'data' in response:
                return response['data']
            return []
        except Exception as e:
            log_error(self.logger, e, "상위 코인 목록 조회 실패")
            return []
    
    def get_coin_price(self, symbol: str) -> Optional[float]:
        """
        코인 가격 조회 (편의 메서드)
        
        Args:
            symbol: 코인 심볼
        
        Returns:
            가격 (USD)
        """
        try:
            response = self.get_asset_by_symbol(symbol)
            if response and 'data' in response:
                return float(response['data']['priceUsd'])
            return None
        except Exception as e:
            log_error(self.logger, e, f"코인 가격 조회 실패: {symbol}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        여러 코인의 가격을 한 번에 조회
        
        Args:
            symbols: 코인 심볼 리스트
        
        Returns:
            심볼별 가격 딕셔너리
        """
        prices = {}
        for symbol in symbols:
            price = self.get_coin_price(symbol)
            if price is not None:
                prices[symbol] = price
        return prices
    
    def collect_data(self, symbols: List[str]) -> Dict[str, Any]:
        """
        BaseCollector 추상 메서드 구현
        
        Args:
            symbols: 코인 심볼 리스트
        
        Returns:
            수집된 데이터
        """
        try:
            data = {}
            for symbol in symbols:
                price = self.get_coin_price(symbol)
                if price is not None:
                    data[symbol] = {
                        'price': price,
                        'source': 'coincap',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
            return data
        except Exception as e:
            log_error(self.logger, e, "CoinCap 데이터 수집 실패")
            return {}
