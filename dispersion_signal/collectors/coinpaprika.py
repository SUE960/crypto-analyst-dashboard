"""
CoinPaprika API 클라이언트
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collectors.base import BaseCollector
from utils.logger import log_error

class CoinPaprikaCollector(BaseCollector):
    """CoinPaprika API 클라이언트"""
    
    def __init__(self):
        super().__init__(
            api_key=None,  # API 키 불필요
            base_url='https://api.coinpaprika.com/v1',
            rate_limit=1000  # 제한 없음
        )
    
    def get_coins(self) -> Optional[List[Dict[str, Any]]]:
        """
        모든 코인 목록 조회
        
        Returns:
            코인 목록
        """
        endpoint = "/coins"
        return self._make_request(endpoint)
    
    def get_tickers(self, quotes: str = 'USD') -> Optional[List[Dict[str, Any]]]:
        """
        모든 코인 티커 조회
        
        Args:
            quotes: 기준 통화
        
        Returns:
            티커 리스트
        """
        endpoint = "/tickers"
        params = {'quotes': quotes}
        return self._make_request(endpoint, params=params)
    
    def get_ticker_by_coin(self, coin_id: str, quotes: str = 'USD') -> Optional[Dict[str, Any]]:
        """
        특정 코인 티커 조회
        
        Args:
            coin_id: 코인 ID
            quotes: 기준 통화
        
        Returns:
            티커 데이터
        """
        endpoint = f"/tickers/{coin_id}"
        params = {'quotes': quotes}
        return self._make_request(endpoint, params=params)
    
    def get_coin_historical(self, coin_id: str, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """
        코인별 히스토리컬 데이터
        
        Args:
            coin_id: 코인 ID
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
        
        Returns:
            히스토리컬 데이터
        """
        endpoint = f"/coins/{coin_id}/ohlcv/historical"
        params = {
            'start': start_date,
            'end': end_date
        }
        return self._make_request(endpoint, params=params)
    
    def get_exchanges(self) -> Optional[List[Dict[str, Any]]]:
        """
        거래소 목록
        
        Returns:
            거래소 목록
        """
        endpoint = "/exchanges"
        return self._make_request(endpoint)
    
    def get_exchange_tickers(self, exchange_id: str, quotes: str = 'USD') -> Optional[List[Dict[str, Any]]]:
        """
        거래소별 코인 티커
        
        Args:
            exchange_id: 거래소 ID
            quotes: 기준 통화
        
        Returns:
            티커 리스트
        """
        endpoint = f"/exchanges/{exchange_id}/tickers"
        params = {'quotes': quotes}
        return self._make_request(endpoint, params=params)
    
    def search_coins(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        코인 검색
        
        Args:
            query: 검색어
        
        Returns:
            검색 결과
        """
        endpoint = "/search"
        params = {'q': query, 'c': 'currencies'}
        return self._make_request(endpoint, params=params)
    
    def get_coin_price(self, coin_id: str) -> Optional[float]:
        """
        코인 가격 조회 (편의 메서드)
        
        Args:
            coin_id: 코인 ID
        
        Returns:
            가격 (USD)
        """
        try:
            ticker = self.get_ticker_by_coin(coin_id)
            if ticker and 'quotes' in ticker:
                return float(ticker['quotes']['USD']['price'])
            return None
        except Exception as e:
            log_error(self.logger, e, f"코인 가격 조회 실패: {coin_id}")
            return None
    
    def get_coin_price_by_symbol(self, symbol: str) -> Optional[float]:
        """
        심볼로 코인 가격 조회 (편의 메서드)
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
        
        Returns:
            가격 (USD)
        """
        try:
            # 먼저 코인 목록에서 해당 심볼 찾기
            coins = self.get_coins()
            if not coins:
                return None
            
            for coin in coins:
                if coin.get('symbol', '').upper() == symbol.upper():
                    return self.get_coin_price(coin['id'])
            
            return None
        except Exception as e:
            log_error(self.logger, e, f"심볼로 코인 가격 조회 실패: {symbol}")
            return None
    
    def get_multiple_prices(self, coin_ids: List[str]) -> Dict[str, float]:
        """
        여러 코인의 가격을 한 번에 조회
        
        Args:
            coin_ids: 코인 ID 리스트
        
        Returns:
            코인 ID별 가격 딕셔너리
        """
        prices = {}
        for coin_id in coin_ids:
            price = self.get_coin_price(coin_id)
            if price is not None:
                prices[coin_id] = price
        return prices
    
    def get_top_coins(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        상위 코인 목록 조회 (편의 메서드)
        
        Args:
            limit: 조회할 코인 수
        
        Returns:
            상위 코인 목록
        """
        try:
            tickers = self.get_tickers()
            if not tickers:
                return []
            
            # 시가총액 순으로 정렬
            sorted_tickers = sorted(tickers, key=lambda x: x.get('market_cap_usd', 0), reverse=True)
            return sorted_tickers[:limit]
        except Exception as e:
            log_error(self.logger, e, "상위 코인 목록 조회 실패")
            return []
    
    def get_exchange_list(self) -> List[str]:
        """
        거래소 ID 목록 조회 (편의 메서드)
        
        Returns:
            거래소 ID 리스트
        """
        try:
            exchanges = self.get_exchanges()
            if not exchanges:
                return []
            
            return [exchange['id'] for exchange in exchanges]
        except Exception as e:
            log_error(self.logger, e, "거래소 목록 조회 실패")
            return []
    
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
                price = self.get_coin_price_by_symbol(symbol)
                if price is not None:
                    data[symbol] = {
                        'price': price,
                        'source': 'coinpaprika',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
            return data
        except Exception as e:
            log_error(self.logger, e, "CoinPaprika 데이터 수집 실패")
            return {}