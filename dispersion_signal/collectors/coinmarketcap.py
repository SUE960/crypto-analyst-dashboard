"""
CoinMarketCap API 클라이언트
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .base import BaseCollector
from utils.logger import log_error

class CoinMarketCapCollector(BaseCollector):
    """CoinMarketCap API 데이터 수집기"""
    
    def __init__(self, api_key: str):
        """
        CoinMarketCap 수집기 초기화
        
        Args:
            api_key: CoinMarketCap API 키
        """
        super().__init__(
            api_key=api_key,
            base_url='https://pro-api.coinmarketcap.com/v1',
            rate_limit=333  # 월 10,000 요청
        )
        
        # CoinMarketCap API 헤더 설정
        self.session.headers['X-CMC_PRO_API_KEY'] = api_key
        self.session.headers['Accept'] = 'application/json'
    
    def get_latest_listings(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        최신 시가총액 상위 코인 조회
        
        Args:
            limit: 조회할 코인 수
        
        Returns:
            상위 코인 리스트
        """
        try:
            endpoint = "/cryptocurrency/listings/latest"
            params = {
                'start': 1,
                'limit': limit,
                'convert': 'USD',
                'sort': 'market_cap',
                'sort_dir': 'desc'
            }
            
            response = self._make_request(endpoint, params)
            
            if not response or 'data' not in response:
                return []
            
            coins = []
            for coin_data in response['data']:
                coin = {
                    'id': coin_data['id'],
                    'symbol': coin_data['symbol'],
                    'name': coin_data['name'],
                    'slug': coin_data['slug'],
                    'market_cap': coin_data['quote']['USD']['market_cap'],
                    'market_cap_rank': coin_data['cmc_rank'],
                    'price': coin_data['quote']['USD']['price'],
                    'volume_24h': coin_data['quote']['USD']['volume_24h'],
                    'percent_change_24h': coin_data['quote']['USD']['percent_change_24h'],
                    'circulating_supply': coin_data['circulating_supply'],
                    'total_supply': coin_data['total_supply'],
                    'max_supply': coin_data['max_supply'],
                    'raw_data': coin_data
                }
                coins.append(coin)
            
            return coins
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, "최신 상위 코인 조회 실패")
            return []
    
    def get_quotes(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        코인별 시세 정보 조회
        
        Args:
            symbols: 코인 심볼 리스트
        
        Returns:
            시세 정보 리스트
        """
        try:
            endpoint = "/cryptocurrency/quotes/latest"
            params = {
                'symbol': ','.join(symbols),
                'convert': 'USD'
            }
            
            response = self._make_request(endpoint, params)
            
            if not response or 'data' not in response:
                return []
            
            quotes = []
            for symbol, coin_data in response['data'].items():
                quote = {
                    'symbol': symbol,
                    'id': coin_data['id'],
                    'name': coin_data['name'],
                    'slug': coin_data['slug'],
                    'market_cap': coin_data['quote']['USD']['market_cap'],
                    'market_cap_rank': coin_data['cmc_rank'],
                    'price': coin_data['quote']['USD']['price'],
                    'volume_24h': coin_data['quote']['USD']['volume_24h'],
                    'percent_change_24h': coin_data['quote']['USD']['percent_change_24h'],
                    'percent_change_7d': coin_data['quote']['USD']['percent_change_7d'],
                    'percent_change_30d': coin_data['quote']['USD']['percent_change_30d'],
                    'percent_change_90d': coin_data['quote']['USD']['percent_change_90d'],
                    'circulating_supply': coin_data['circulating_supply'],
                    'total_supply': coin_data['total_supply'],
                    'max_supply': coin_data['max_supply'],
                    'fully_diluted_market_cap': coin_data['quote']['USD']['fully_diluted_market_cap'],
                    'raw_data': coin_data
                }
                quotes.append(quote)
            
            return quotes
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"시세 정보 조회 실패: {symbols}")
            return []
    
    def get_global_metrics(self) -> Optional[Dict[str, Any]]:
        """
        글로벌 암호화폐 메트릭 조회
        
        Returns:
            글로벌 메트릭 데이터 또는 None
        """
        try:
            endpoint = "/global-metrics/quotes/latest"
            params = {
                'convert': 'USD'
            }
            
            response = self._make_request(endpoint, params)
            
            if not response or 'data' not in response:
                return None
            
            data = response['data']
            quote = data['quote']['USD']
            
            global_metrics = {
                'timestamp': datetime.now(timezone.utc),
                'total_market_cap': quote.get('total_market_cap'),
                'total_volume_24h': quote.get('total_volume_24h'),
                'btc_dominance': data.get('btc_dominance'),
                'eth_dominance': data.get('eth_dominance'),
                'active_cryptocurrencies': data.get('active_cryptocurrencies'),
                'active_exchanges': data.get('active_exchanges'),
                'active_market_pairs': data.get('active_market_pairs'),
                'raw_data': data
            }
            
            return global_metrics
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, "글로벌 메트릭 조회 실패")
            return None
    
    def collect_market_cap_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        여러 코인의 시가총액 데이터 수집
        
        Args:
            symbols: 코인 심볼 리스트
        
        Returns:
            시가총액 데이터 리스트
        """
        try:
            all_data = []
            
            # 시세 정보 조회
            quotes = self.get_quotes(symbols)
            
            for quote in quotes:
                # 데이터 변환
                converted_data = self._convert_quote_to_market_cap_data(quote)
                if converted_data:
                    all_data.append(converted_data)
            
            return all_data
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, "시가총액 데이터 수집 실패")
            return []
    
    def collect_global_metrics_data(self) -> Optional[Dict[str, Any]]:
        """
        글로벌 메트릭 데이터 수집
        
        Returns:
            글로벌 메트릭 데이터 또는 None
        """
        try:
            return self.get_global_metrics()
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, "글로벌 메트릭 데이터 수집 실패")
            return None
    
    def _convert_quote_to_market_cap_data(self, quote: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        시세 정보를 시가총액 데이터 형식으로 변환
        
        Args:
            quote: CoinMarketCap API 시세 응답
        
        Returns:
            변환된 데이터 또는 None
        """
        try:
            timestamp = datetime.now(timezone.utc)
            
            return {
                'symbol': quote['symbol'],
                'timestamp': timestamp,
                'market_cap': quote['market_cap'],
                'market_cap_rank': quote['market_cap_rank'],
                'fully_diluted_market_cap': quote['fully_diluted_market_cap'],
                'circulating_supply': quote['circulating_supply'],
                'total_supply': quote['total_supply'],
                'max_supply': quote['max_supply'],
                'market_cap_dominance': None,  # 개별 코인에는 없음
                'ath_price': None,  # 별도 API 호출 필요
                'ath_date': None,
                'ath_change_percentage': None,
                'atl_price': None,
                'atl_date': None,
                'atl_change_percentage': None,
                'data_source': 'coinmarketcap',
                'raw_data': quote['raw_data']
            }
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"시세 데이터 변환 실패: {quote.get('symbol', 'Unknown')}")
            return None
    
    def collect_data(self, symbol: str, start_date: datetime, end_date: datetime, interval: str = '1d') -> List[Dict[str, Any]]:
        """
        베이스 클래스의 추상 메서드 구현
        
        Args:
            symbol: 코인 심볼
            start_date: 시작 날짜
            end_date: 종료 날짜
            interval: 데이터 간격
        
        Returns:
            수집된 데이터 리스트
        """
        try:
            # CoinMarketCap은 실시간 데이터만 제공
            quotes = self.get_quotes([symbol])
            
            if not quotes:
                return []
            
            converted_data = self._convert_quote_to_market_cap_data(quotes[0])
            return [converted_data] if converted_data else []
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"데이터 수집 실패: {symbol}")
            return []
