"""
Supabase 클라이언트 및 데이터베이스 작업 (Phase 2)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
import logging
from supabase import create_client, Client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .models_phase2 import (
    MarketCapData, SocialData, NewsSentiment, GlobalMetrics,
    CryptocurrencyBinance, MarketDataDaily, PriceHistory, CurrentPrice
)
from utils.logger import log_error

class SupabaseClientPhase2:
    """Supabase 데이터베이스 클라이언트 (Phase 2)"""
    
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
            symbol: 코인 심볼 (예: 'BTC')
        
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
    
    def insert_market_cap_data(self, market_cap_data: List[MarketCapData]) -> bool:
        """
        시가총액 데이터 배치 삽입
        
        Args:
            market_cap_data: 시가총액 데이터 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for data_point in market_cap_data:
                data_dict = data_point.dict()
                data_dict['crypto_id'] = str(data_dict['crypto_id'])
                
                # Decimal을 float로 변환
                for key, value in data_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        data_dict[key] = float(value)
                    elif isinstance(value, datetime):
                        data_dict[key] = value.isoformat()
                
                data.append(data_dict)
            
            response = self.client.table('market_cap_data')\
                .upsert(data, on_conflict='crypto_id,timestamp,data_source')\
                .execute()
            
            self.logger.info(f"시가총액 데이터 {len(market_cap_data)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "시가총액 데이터 삽입 실패")
            return False
    
    def insert_social_data(self, social_data: List[SocialData]) -> bool:
        """
        소셜 데이터 배치 삽입
        
        Args:
            social_data: 소셜 데이터 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for data_point in social_data:
                data_dict = data_point.dict()
                data_dict['crypto_id'] = str(data_dict['crypto_id'])
                
                # Decimal을 float로 변환
                for key, value in data_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        data_dict[key] = float(value)
                    elif isinstance(value, datetime):
                        data_dict[key] = value.isoformat()
                
                data.append(data_dict)
            
            response = self.client.table('social_data')\
                .upsert(data, on_conflict='crypto_id,timestamp,data_source')\
                .execute()
            
            self.logger.info(f"소셜 데이터 {len(social_data)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "소셜 데이터 삽입 실패")
            return False
    
    def insert_news_sentiment(self, news_sentiment: List[NewsSentiment]) -> bool:
        """
        뉴스 감성 데이터 배치 삽입
        
        Args:
            news_sentiment: 뉴스 감성 데이터 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for data_point in news_sentiment:
                data_dict = data_point.dict()
                data_dict['crypto_id'] = str(data_dict['crypto_id'])
                
                # Decimal을 float로 변환
                for key, value in data_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        data_dict[key] = float(value)
                    elif isinstance(value, datetime):
                        data_dict[key] = value.isoformat()
                
                data.append(data_dict)
            
            response = self.client.table('news_sentiment')\
                .upsert(data, on_conflict='crypto_id,timestamp,data_source')\
                .execute()
            
            self.logger.info(f"뉴스 감성 데이터 {len(news_sentiment)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "뉴스 감성 데이터 삽입 실패")
            return False
    
    def insert_global_metrics(self, global_metrics: GlobalMetrics) -> bool:
        """
        글로벌 메트릭 데이터 삽입
        
        Args:
            global_metrics: 글로벌 메트릭 데이터
        
        Returns:
            성공 여부
        """
        try:
            data_dict = global_metrics.dict()
            
            # Decimal을 float로 변환
            for key, value in data_dict.items():
                if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                    data_dict[key] = float(value)
                elif isinstance(value, datetime):
                    data_dict[key] = value.isoformat()
            
            response = self.client.table('global_metrics')\
                .upsert([data_dict], on_conflict='timestamp,data_source')\
                .execute()
            
            self.logger.info("글로벌 메트릭 데이터 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "글로벌 메트릭 데이터 삽입 실패")
            return False
    
    def get_latest_market_cap_data(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 시가총액 데이터 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            시가총액 데이터 리스트
        """
        try:
            response = self.client.table('market_cap_data')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"시가총액 데이터 조회 실패: {crypto_id}")
            return []
    
    def get_latest_social_data(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 소셜 데이터 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            소셜 데이터 리스트
        """
        try:
            response = self.client.table('social_data')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"소셜 데이터 조회 실패: {crypto_id}")
            return []
    
    def get_latest_news_sentiment(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 뉴스 감성 데이터 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            뉴스 감성 데이터 리스트
        """
        try:
            response = self.client.table('news_sentiment')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"뉴스 감성 데이터 조회 실패: {crypto_id}")
            return []
    
    def get_latest_global_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 글로벌 메트릭 조회
        
        Args:
            limit: 조회할 레코드 수
        
        Returns:
            글로벌 메트릭 리스트
        """
        try:
            response = self.client.table('global_metrics')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, "글로벌 메트릭 조회 실패")
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
            
            # 시가총액 데이터 수
            marketcap_response = self.client.table('market_cap_data')\
                .select('count')\
                .execute()
            summary['total_marketcap_records'] = marketcap_response.data[0]['count'] if marketcap_response.data else 0
            
            # 소셜 데이터 수
            social_response = self.client.table('social_data')\
                .select('count')\
                .execute()
            summary['total_social_records'] = social_response.data[0]['count'] if social_response.data else 0
            
            # 뉴스 감성 데이터 수
            news_response = self.client.table('news_sentiment')\
                .select('count')\
                .execute()
            summary['total_news_records'] = news_response.data[0]['count'] if news_response.data else 0
            
            # 글로벌 메트릭 수
            global_response = self.client.table('global_metrics')\
                .select('count')\
                .execute()
            summary['total_global_records'] = global_response.data[0]['count'] if global_response.data else 0
            
            return summary
            
        except Exception as e:
            log_error(self.logger, e, "데이터 요약 조회 실패")
            return {}
