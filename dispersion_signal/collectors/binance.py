"""
Binance API 클라이언트 (무료)
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .base import BaseCollector
from utils.logger import log_error

class BinanceCollector(BaseCollector):
    """Binance API 데이터 수집기 (무료)"""
    
    def __init__(self):
        """
        Binance 수집기 초기화
        
        API 키 불필요 - 공개 엔드포인트 사용
        """
        super().__init__(
            api_key='public',  # 공개 엔드포인트
            base_url='https://api.binance.com',
            rate_limit=1200  # 분당 1200 요청 (매우 관대함)
        )
        
        # Binance API는 Authorization 헤더 불필요
        self.session.headers.pop('Authorization', None)
    
    def get_top_coins(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        거래량 기준 상위 코인 조회
        
        Args:
            limit: 조회할 코인 수
        
        Returns:
            상위 코인 리스트
        """
        try:
            endpoint = "/api/v3/ticker/24hr"
            response = self._make_request(endpoint)
            
            if not response:
                return []
            
            # USDT 페어만 필터링하고 거래량 기준으로 정렬
            usdt_pairs = [item for item in response if item['symbol'].endswith('USDT')]
            usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
            
            # 상위 코인만 반환
            top_coins = []
            for i, coin in enumerate(usdt_pairs[:limit], 1):
                symbol = coin['symbol'].replace('USDT', '')
                top_coins.append({
                    'symbol': symbol,
                    'name': self._get_coin_name(symbol),
                    'binance_symbol': coin['symbol'],
                    'market_cap_rank': i,
                    'quote_volume': float(coin['quoteVolume']),
                    'last_price': float(coin['lastPrice']),
                    'price_change_percent': float(coin['priceChangePercent']),
                    'raw_data': coin
                })
            
            return top_coins
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, "상위 코인 조회 실패")
            return []
    
    def get_24hr_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        24시간 가격/거래량 데이터 조회
        
        Args:
            symbol: 코인 심볼 (예: 'BTCUSDT')
        
        Returns:
            24시간 데이터 또는 None
        """
        try:
            endpoint = f"/api/v3/ticker/24hr?symbol={symbol}"
            response = self._make_request(endpoint)
            
            if response:
                return {
                    'symbol': symbol,
                    'data': response,
                    'endpoint': endpoint,
                    'raw_response': response
                }
            return None
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"24시간 데이터 조회 실패: {symbol}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        현재 가격 조회
        
        Args:
            symbol: 코인 심볼 (예: 'BTCUSDT')
        
        Returns:
            현재 가격 데이터 또는 None
        """
        try:
            endpoint = f"/api/v3/ticker/price?symbol={symbol}"
            response = self._make_request(endpoint)
            
            if response:
                return {
                    'symbol': symbol,
                    'data': response,
                    'endpoint': endpoint,
                    'raw_response': response
                }
            return None
            
        except Exception as e:
            log_error(logger, e, f"현재 가격 조회 실패: {symbol}")
            return None
    
    def get_historical_klines(self, symbol: str, start_date: datetime, end_date: datetime, interval: str = '1d') -> Optional[Dict[str, Any]]:
        """
        히스토리컬 캔들 데이터 조회
        
        Args:
            symbol: 코인 심볼 (예: 'BTCUSDT')
            start_date: 시작 날짜
            end_date: 종료 날짜
            interval: 캔들 간격 (1d, 1h, 1m 등)
        
        Returns:
            히스토리컬 데이터 또는 None
        """
        try:
            # Binance API는 최대 1000개 캔들 제한
            # 1년치 데이터를 위해 여러 번 요청해야 할 수 있음
            
            start_time = int(start_date.timestamp() * 1000)
            end_time = int(end_date.timestamp() * 1000)
            
            endpoint = f"/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'startTime': start_time,
                'endTime': end_time,
                'limit': 1000  # 최대 제한
            }
            
            response = self._make_request(endpoint, params)
            
            if response:
                return {
                    'symbol': symbol,
                    'data': response,
                    'endpoint': endpoint,
                    'raw_response': response,
                    'start_time': start_time,
                    'end_time': end_time,
                    'interval': interval
                }
            return None
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"히스토리컬 데이터 조회 실패: {symbol}")
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
            # 일일 데이터와 히스토리컬 데이터를 모두 수집
            all_data = []
            
            # 24시간 데이터 수집
            ticker_data = self.get_24hr_ticker(symbol)
            if ticker_data:
                converted_data = self._convert_24hr_data(ticker_data['data'], symbol)
                if converted_data:
                    all_data.append(converted_data)
            
            # 히스토리컬 데이터 수집
            klines_data = self.get_historical_klines(symbol, start_date, end_date, interval)
            if klines_data:
                converted_data = self._convert_klines_data(klines_data['data'], symbol)
                if converted_data:
                    all_data.extend(converted_data)
            
            return all_data
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"데이터 수집 실패: {symbol}")
            return []
    
    def collect_daily_data(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        여러 코인의 일일 데이터 수집
        
        Args:
            symbols: 코인 심볼 리스트
        
        Returns:
            수집된 데이터 리스트
        """
        try:
            all_data = []
            
            for symbol in symbols:
                # 24시간 데이터 수집
                ticker_data = self.get_24hr_ticker(symbol)
                if ticker_data:
                    # 데이터 변환
                    converted_data = self._convert_24hr_data(ticker_data['data'], symbol)
                    if converted_data:
                        all_data.append(converted_data)
                
                # Rate limit 고려하여 잠시 대기
                time.sleep(0.1)
            
            return all_data
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, "일일 데이터 수집 실패")
            return []
    
    def collect_historical_data(self, symbols: List[str], days: int = 365) -> List[Dict[str, Any]]:
        """
        여러 코인의 히스토리컬 데이터 수집
        
        Args:
            symbols: 코인 심볼 리스트
            days: 수집할 일수
        
        Returns:
            수집된 히스토리컬 데이터 리스트
        """
        try:
            all_data = []
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            for symbol in symbols:
                # 히스토리컬 데이터 수집
                klines_data = self.get_historical_klines(symbol, start_date, end_date, '1d')
                if klines_data:
                    # 데이터 변환
                    converted_data = self._convert_klines_data(klines_data['data'], symbol)
                    if converted_data:
                        all_data.extend(converted_data)
                
                # Rate limit 고려하여 잠시 대기
                time.sleep(0.1)
            
            return all_data
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, "히스토리컬 데이터 수집 실패")
            return []
    
    def _convert_24hr_data(self, data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
        """
        24시간 데이터를 데이터베이스 형식으로 변환
        
        Args:
            data: Binance API 응답 데이터
            symbol: 코인 심볼
        
        Returns:
            변환된 데이터 또는 None
        """
        try:
            # 현재 날짜 (UTC 기준)
            current_date = datetime.now().date()
            
            return {
                'symbol': symbol,
                'date': current_date,
                'open_price': float(data['openPrice']),
                'high_price': float(data['highPrice']),
                'low_price': float(data['lowPrice']),
                'close_price': float(data['lastPrice']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume']),
                'price_change_24h': float(data['priceChange']),
                'price_change_percent_24h': float(data['priceChangePercent']),
                'weighted_avg_price': float(data['weightedAvgPrice']),
                'prev_close_price': float(data['prevClosePrice']),
                'last_price': float(data['lastPrice']),
                'bid_price': float(data['bidPrice']),
                'ask_price': float(data['askPrice']),
                'trade_count': int(data['count']),
                'first_trade_id': int(data['firstId']),
                'last_trade_id': int(data['lastId']),
                'open_time': datetime.fromtimestamp(int(data['openTime']) / 1000),
                'close_time': datetime.fromtimestamp(int(data['closeTime']) / 1000),
                'data_source': 'binance',
                'raw_data': data
            }
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"24시간 데이터 변환 실패: {symbol}")
            return None
    
    def _convert_klines_data(self, data: List[List], symbol: str) -> List[Dict[str, Any]]:
        """
        캔들 데이터를 데이터베이스 형식으로 변환
        
        Args:
            data: Binance API 캔들 데이터
            symbol: 코인 심볼
        
        Returns:
            변환된 데이터 리스트
        """
        try:
            converted_data = []
            
            for kline in data:
                # 캔들 데이터 구조: [시작시간, 시가, 고가, 저가, 종가, 거래량, 종료시간, 거래량(USDT), 거래수, 매수거래량, 매수거래량(USDT), 무시]
                timestamp = datetime.fromtimestamp(int(kline[0]) / 1000, tz=None)
                # UTC timezone 추가
                timestamp = timestamp.replace(tzinfo=None)  # timezone 정보 제거 후 다시 추가
                from datetime import timezone
                timestamp = timestamp.replace(tzinfo=timezone.utc)
                
                converted_data.append({
                    'symbol': symbol,
                    'timestamp': timestamp,
                    'open_price': float(kline[1]),
                    'high_price': float(kline[2]),
                    'low_price': float(kline[3]),
                    'close_price': float(kline[4]),
                    'volume': float(kline[5]),
                    'quote_volume': float(kline[7]),
                    'trade_count': int(kline[8]),
                    'taker_buy_volume': float(kline[9]),
                    'taker_buy_quote_volume': float(kline[10]),
                    'data_source': 'binance',
                    'raw_data': {
                        'kline': kline,
                        'symbol': symbol,
                        'timestamp': timestamp.isoformat()
                    }
                })
            
            return converted_data
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            log_error(logger, e, f"캔들 데이터 변환 실패: {symbol}")
            return []
    
    def _get_coin_name(self, symbol: str) -> str:
        """
        코인 심볼로부터 이름 추출
        
        Args:
            symbol: 코인 심볼
        
        Returns:
            코인 이름
        """
        coin_names = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'USDC': 'USD Coin',
            'SOL': 'Solana',
            'XRP': 'Ripple',
            'BNB': 'BNB',
            'ZEC': 'Zcash',
            'FDUSD': 'First Digital USD',
            'GIGGLE': 'Giggle',
            'DOGE': 'Dogecoin',
            'VIRTUAL': 'Virtual',
            'ASTER': 'Aster',
            'TRX': 'TRON',
            'SUI': 'Sui',
            'AIXBT': 'AIXBT',
            'USDE': 'USDE',
            'XPL': 'XPL',
            'PUMP': 'Pump',
            'TAO': 'Bittensor',
            'AVAX': 'Avalanche'
        }
        
        return coin_names.get(symbol, symbol)
