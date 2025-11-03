"""
CoinGecko API 클라이언트
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collectors.base import BaseCollector
from utils.logger import log_error

class CoinGeckoCollector(BaseCollector):
    """CoinGecko API 클라이언트"""
    
    # 주요 코인 심볼-ID 매핑
    SYMBOL_TO_ID_MAP = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'SOL': 'solana',
        'XRP': 'ripple',
        'BNB': 'binancecoin',
        'DOGE': 'dogecoin',
        'TRX': 'tron',
        'SUI': 'sui',
        'AVAX': 'avalanche-2',
        'TAO': 'bittensor',
        'USDC': 'usd-coin',
        'USDT': 'tether',
        'ADA': 'cardano',
        'MATIC': 'matic-network',
        'DOT': 'polkadot',
        'LINK': 'chainlink',
        'UNI': 'uniswap',
        'LTC': 'litecoin',
        'BCH': 'bitcoin-cash',
        'ATOM': 'cosmos',
        'FTM': 'fantom',
        'NEAR': 'near',
        'ALGO': 'algorand',
        'VET': 'vechain',
        'ICP': 'internet-computer',
        'FIL': 'filecoin',
        'THETA': 'theta-token',
        'EOS': 'eos',
        'AAVE': 'aave',
        'SUSHI': 'sushi',
        'COMP': 'compound-governance-token',
        'MKR': 'maker',
        'YFI': 'yearn-finance',
        'SNX': 'havven',
        'UMA': 'uma',
        'BAL': 'balancer',
        'CRV': 'curve-dao-token',
        '1INCH': '1inch',
        'ZEC': 'zcash',
        'FDUSD': 'first-digital-usd',
        'GIGGLE': 'giggle',
        'VIRTUAL': 'virtual-protocol',
        'ASTER': 'aster',
        'AIXBT': 'aixbt',
        'USDE': 'energi-dollar',
        'PUMP': 'pump-fun',
        'XPL': 'xpl',
    }
    
    def __init__(self):
        super().__init__(
            api_key=None,  # 무료 티어는 API 키 불필요
            base_url='https://api.coingecko.com/api/v3',
            rate_limit=30  # 분당 30회 제한
        )
    
    def get_coins_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        모든 코인 목록 조회
        
        Returns:
            코인 목록
        """
        endpoint = "/coins/list"
        return self._make_request(endpoint)
    
    def get_coins_markets(self, vs_currency: str = 'usd', 
                         per_page: int = 100, page: int = 1) -> Optional[List[Dict[str, Any]]]:
        """
        코인별 시장 데이터
        
        Args:
            vs_currency: 기준 통화 (usd, btc, eth 등)
            per_page: 페이지당 항목 수
            page: 페이지 번호
        
        Returns:
            시장 데이터 리스트
        """
        endpoint = "/coins/markets"
        params = {
            'vs_currency': vs_currency,
            'order': 'market_cap_desc',
            'per_page': per_page,
            'page': page,
            'sparkline': False,
            'price_change_percentage': '24h,7d,30d'
        }
        return self._make_request(endpoint, params=params)
    
    def get_coin_by_id(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 코인 상세 정보
        
        Args:
            coin_id: 코인 ID (예: 'bitcoin')
        
        Returns:
            코인 상세 정보
        """
        endpoint = f"/coins/{coin_id}"
        params = {
            'localization': False,
            'tickers': True,
            'market_data': True,
            'community_data': True,
            'developer_data': True,
            'sparkline': False
        }
        return self._make_request(endpoint, params=params)
    
    def get_coin_market_chart(self, coin_id: str, vs_currency: str = 'usd', 
                            days: int = 30) -> Optional[Dict[str, Any]]:
        """
        코인별 히스토리컬 차트 데이터
        
        Args:
            coin_id: 코인 ID
            vs_currency: 기준 통화
            days: 조회할 일수
        
        Returns:
            차트 데이터
        """
        endpoint = f"/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': vs_currency,
            'days': days,
            'interval': 'daily' if days > 1 else 'hourly'
        }
        return self._make_request(endpoint, params=params)
    
    def get_exchanges(self, per_page: int = 100, page: int = 1) -> Optional[List[Dict[str, Any]]]:
        """
        거래소 목록
        
        Args:
            per_page: 페이지당 항목 수
            page: 페이지 번호
        
        Returns:
            거래소 목록
        """
        endpoint = "/exchanges"
        params = {
            'per_page': per_page,
            'page': page
        }
        return self._make_request(endpoint, params=params)
    
    def get_global(self) -> Optional[Dict[str, Any]]:
        """
        글로벌 암호화폐 데이터
        
        Returns:
            글로벌 데이터
        """
        endpoint = "/global"
        return self._make_request(endpoint)
    
    def search_coins(self, query: str) -> Optional[Dict[str, Any]]:
        """
        코인 검색
        
        Args:
            query: 검색어
        
        Returns:
            검색 결과
        """
        endpoint = "/search"
        params = {'query': query}
        return self._make_request(endpoint, params=params)
    
    def get_trending_coins(self) -> Optional[Dict[str, Any]]:
        """
        트렌딩 코인 조회
        
        Returns:
            트렌딩 코인 데이터
        """
        endpoint = "/search/trending"
        return self._make_request(endpoint)
    
    def get_coin_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        심볼로 코인 정보 조회
        
        Args:
            symbol: 코인 심볼 (예: 'BTC')
        
        Returns:
            코인 정보
        """
        try:
            # 먼저 코인 목록에서 해당 심볼 찾기
            coins = self.get_coins_list()
            if not coins:
                return None
            
            for coin in coins:
                if coin.get('symbol', '').upper() == symbol.upper():
                    return self.get_coin_by_id(coin['id'])
            
            return None
        except Exception as e:
            log_error(self.logger, e, f"심볼로 코인 조회 실패: {symbol}")
            return None
    
    def get_top_coins(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        상위 코인 목록 조회 (편의 메서드)
        
        Args:
            limit: 조회할 코인 수
        
        Returns:
            상위 코인 목록
        """
        try:
            markets = self.get_coins_markets(per_page=limit)
            if not markets:
                return []
            
            return markets
        except Exception as e:
            log_error(self.logger, e, "상위 코인 목록 조회 실패")
            return []
    
    def get_coin_price(self, coin_id: str) -> Optional[float]:
        """
        코인 가격 조회 (편의 메서드)
        
        Args:
            coin_id: 코인 ID
        
        Returns:
            가격 (USD)
        """
        try:
            coin_data = self.get_coin_by_id(coin_id)
            if coin_data and 'market_data' in coin_data:
                return float(coin_data['market_data']['current_price']['usd'])
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
            # 먼저 매핑 딕셔너리에서 ID 확인
            coin_id = self.SYMBOL_TO_ID_MAP.get(symbol.upper())
            if coin_id:
                return self.get_coin_price(coin_id)
            
            # 매핑이 없으면 코인 목록에서 검색 (시가총액 기준 정렬)
            markets = self.get_coins_markets(per_page=250)  # 상위 250개 코인만 검색
            if not markets:
                return None
            
            # 심볼이 일치하는 코인 찾기 (시가총액 순으로 정렬되어 있음)
            for coin in markets:
                if coin.get('symbol', '').upper() == symbol.upper():
                    return coin.get('current_price')
            
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
    
    def get_coin_simple_price(self, ids: List[str], vs_currencies: List[str] = ['usd']) -> Optional[Dict[str, Any]]:
        """
        간단한 가격 조회 (여러 코인 한 번에)
        
        Args:
            ids: 코인 ID 리스트
            vs_currencies: 기준 통화 리스트
        
        Returns:
            가격 데이터
        """
        endpoint = "/simple/price"
        params = {
            'ids': ','.join(ids),
            'vs_currencies': ','.join(vs_currencies),
            'include_market_cap': True,
            'include_24hr_vol': True,
            'include_24hr_change': True
        }
        return self._make_request(endpoint, params=params)
    
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
                        'source': 'coingecko',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
            return data
        except Exception as e:
            log_error(self.logger, e, "CoinGecko 데이터 수집 실패")
            return {}