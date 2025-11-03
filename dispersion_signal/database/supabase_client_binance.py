"""
Supabase 클라이언트 및 데이터베이스 작업 (Binance API 버전)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from uuid import UUID
import logging
from supabase import create_client, Client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .models_binance import (
    CryptocurrencyBinance, MarketDataDaily, PriceHistory, 
    CurrentPrice, TopCoin, SentimentMetric, DerivativesMetric, DispersionScore
)
from utils.logger import log_error

class SupabaseClientBinance:
    """Supabase 데이터베이스 클라이언트 (Binance API 버전)"""
    
    def __init__(self, url: str, service_role_key: str):
        """
        Supabase 클라이언트 초기화
        
        Args:
            url: Supabase 프로젝트 URL
            service_role_key: Service Role 키
        """
        self.client: Client = create_client(url, service_role_key)
        self.logger = logging.getLogger(__name__)
    
    def get_crypto_id(self, symbol: str) -> Optional[UUID]:
        """
        코인 심볼로 crypto_id 조회
        
        Args:
            symbol: 코인 심볼 (예: 'BTC' 또는 'BTCUSDT')
        
        Returns:
            crypto_id 또는 None
        """
        try:
            # USDT 접미사 제거 (BTCUSDT -> BTC)
            clean_symbol = symbol.replace('USDT', '') if symbol.endswith('USDT') else symbol
            
            response = self.client.table('cryptocurrencies')\
                .select('id')\
                .eq('symbol', clean_symbol.upper())\
                .eq('is_active', True)\
                .execute()
            
            if response.data:
                return UUID(response.data[0]['id'])
            return None
            
        except Exception as e:
            log_error(self.logger, e, f"crypto_id 조회 실패: {symbol}")
            return None
    
    def upsert_cryptocurrencies(self, coins: List[TopCoin]) -> bool:
        """
        코인 마스터 데이터 업서트
        
        Args:
            coins: 상위 코인 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for coin in coins:
                coin_dict = {
                    'symbol': coin.symbol,
                    'name': coin.name,
                    'binance_symbol': coin.binance_symbol,
                    'market_cap_rank': coin.market_cap_rank,
                    'is_active': True
                }
                data.append(coin_dict)
            
            response = self.client.table('cryptocurrencies')\
                .upsert(data, on_conflict='symbol')\
                .execute()
            
            self.logger.info(f"코인 마스터 데이터 {len(coins)}개 업서트 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "코인 마스터 데이터 업서트 실패")
            return False
    
    def insert_market_data_daily(self, market_data: List[MarketDataDaily]) -> bool:
        """
        일일 시장 데이터 배치 삽입
        
        Args:
            market_data: 일일 시장 데이터 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for data_point in market_data:
                data_dict = data_point.dict()
                data_dict['crypto_id'] = str(data_dict['crypto_id'])
                
                # Decimal을 float로 변환
                for key, value in data_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        data_dict[key] = float(value)
                    elif isinstance(value, date):
                        data_dict[key] = value.isoformat()
                    elif isinstance(value, datetime):
                        data_dict[key] = value.isoformat()
                
                data.append(data_dict)
            
            response = self.client.table('market_data_daily')\
                .upsert(data, on_conflict='crypto_id,date,data_source')\
                .execute()
            
            self.logger.info(f"일일 시장 데이터 {len(market_data)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "일일 시장 데이터 삽입 실패")
            return False
    
    def insert_price_history(self, price_history: List[PriceHistory]) -> bool:
        """
        히스토리컬 가격 데이터 배치 삽입
        
        Args:
            price_history: 히스토리컬 가격 데이터 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for price_point in price_history:
                price_dict = price_point.dict()
                price_dict['crypto_id'] = str(price_dict['crypto_id'])
                
                # Decimal을 float로 변환
                for key, value in price_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        price_dict[key] = float(value)
                    elif isinstance(value, datetime):
                        price_dict[key] = value.isoformat()
                
                data.append(price_dict)
            
            response = self.client.table('price_history')\
                .upsert(data, on_conflict='crypto_id,timestamp,data_source')\
                .execute()
            
            self.logger.info(f"히스토리컬 가격 데이터 {len(price_history)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "히스토리컬 가격 데이터 삽입 실패")
            return False
    
    def insert_current_prices(self, current_prices: List[CurrentPrice]) -> bool:
        """
        현재 가격 데이터 배치 삽입
        
        Args:
            current_prices: 현재 가격 데이터 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for price_point in current_prices:
                price_dict = price_point.dict()
                price_dict['crypto_id'] = str(price_dict['crypto_id'])
                
                # Decimal을 float로 변환
                for key, value in price_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        price_dict[key] = float(value)
                    elif isinstance(value, datetime):
                        price_dict[key] = value.isoformat()
                
                data.append(price_dict)
            
            response = self.client.table('current_prices')\
                .upsert(data, on_conflict='crypto_id,timestamp,data_source')\
                .execute()
            
            self.logger.info(f"현재 가격 데이터 {len(current_prices)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "현재 가격 데이터 삽입 실패")
            return False
    
    def get_latest_market_data(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 일일 시장 데이터 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            일일 시장 데이터 리스트
        """
        try:
            response = self.client.table('market_data_daily')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('date', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"일일 시장 데이터 조회 실패: {crypto_id}")
            return []
    
    def get_latest_price_history(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 히스토리컬 가격 데이터 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            히스토리컬 가격 데이터 리스트
        """
        try:
            response = self.client.table('price_history')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"히스토리컬 가격 데이터 조회 실패: {crypto_id}")
            return []
    
    def get_crypto_list(self) -> List[Dict[str, Any]]:
        """
        활성 코인 목록 조회
        
        Returns:
            코인 목록
        """
        try:
            response = self.client.table('cryptocurrencies')\
                .select('*')\
                .eq('is_active', True)\
                .order('market_cap_rank')\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, "코인 목록 조회 실패")
            return []
    
    def get_top_coins(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        시가총액 상위 코인 조회
        
        Args:
            limit: 조회할 코인 수
        
        Returns:
            상위 코인 리스트
        """
        try:
            response = self.client.table('cryptocurrencies')\
                .select('*')\
                .eq('is_active', True)\
                .order('market_cap_rank')\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, "상위 코인 조회 실패")
            return []
    
    def test_connection(self) -> bool:
        """
        Supabase 연결 테스트
        
        Returns:
            연결 성공 여부
        """
        try:
            response = self.client.table('cryptocurrencies')\
                .select('count')\
                .execute()
            
            self.logger.info("Supabase 연결 성공")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "Supabase 연결 실패")
            return False
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        데이터베이스 요약 정보 조회
        
        Returns:
            데이터 요약 정보
        """
        try:
            summary = {}
            
            # 코인 수
            crypto_response = self.client.table('cryptocurrencies')\
                .select('count')\
                .execute()
            summary['total_coins'] = crypto_response.data[0]['count'] if crypto_response.data else 0
            
            # 일일 데이터 수
            daily_response = self.client.table('market_data_daily')\
                .select('count')\
                .execute()
            summary['total_daily_records'] = daily_response.data[0]['count'] if daily_response.data else 0
            
            # 히스토리컬 데이터 수
            history_response = self.client.table('price_history')\
                .select('count')\
                .execute()
            summary['total_history_records'] = history_response.data[0]['count'] if history_response.data else 0
            
            # 현재 가격 데이터 수
            current_response = self.client.table('current_prices')\
                .select('count')\
                .execute()
            summary['total_current_records'] = current_response.data[0]['count'] if current_response.data else 0
            
            return summary
            
        except Exception as e:
            log_error(self.logger, e, "데이터 요약 조회 실패")
            return {}
