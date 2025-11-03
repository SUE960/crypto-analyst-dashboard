"""
Supabase 클라이언트 및 데이터베이스 작업 (CoinGecko 버전)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
import logging
from supabase import create_client, Client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .models_coingecko import MarketMetric, PriceHistory, ExchangeData, SentimentMetric, DerivativesMetric, DispersionScore, Cryptocurrency
from utils.logger import log_error

class SupabaseClient:
    """Supabase 데이터베이스 클라이언트 (CoinGecko 버전)"""
    
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
            response = self.client.table('cryptocurrencies')\
                .select('id')\
                .eq('symbol', symbol.upper())\
                .eq('is_active', True)\
                .execute()
            
            if response.data:
                return UUID(response.data[0]['id'])
            return None
            
        except Exception as e:
            log_error(self.logger, e, f"crypto_id 조회 실패: {symbol}")
            return None
    
    def insert_market_metrics(self, metrics: List[MarketMetric]) -> bool:
        """
        시장 메트릭 데이터 배치 삽입
        
        Args:
            metrics: 시장 메트릭 리스트
        
        Returns:
            성공 여부
        """
        try:
            # Pydantic 모델을 딕셔너리로 변환
            data = []
            for metric in metrics:
                metric_dict = metric.dict()
                # UUID를 문자열로 변환
                metric_dict['crypto_id'] = str(metric_dict['crypto_id'])
                # Decimal을 float로 변환
                for key, value in metric_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        metric_dict[key] = float(value)
                data.append(metric_dict)
            
            # 배치 삽입 (upsert 사용)
            response = self.client.table('market_metrics')\
                .upsert(data, on_conflict='crypto_id,timestamp,data_source')\
                .execute()
            
            self.logger.info(f"시장 메트릭 {len(metrics)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "시장 메트릭 삽입 실패")
            return False
    
    def insert_price_history(self, prices: List[PriceHistory]) -> bool:
        """
        가격 히스토리 데이터 배치 삽입
        
        Args:
            prices: 가격 히스토리 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for price in prices:
                price_dict = price.dict()
                price_dict['crypto_id'] = str(price_dict['crypto_id'])
                # Decimal을 float로 변환
                for key, value in price_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        price_dict[key] = float(value)
                data.append(price_dict)
            
            response = self.client.table('price_history')\
                .upsert(data, on_conflict='crypto_id,timestamp,data_source')\
                .execute()
            
            self.logger.info(f"가격 히스토리 {len(prices)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "가격 히스토리 삽입 실패")
            return False
    
    def insert_exchange_data(self, exchanges: List[ExchangeData]) -> bool:
        """
        거래소 데이터 배치 삽입
        
        Args:
            exchanges: 거래소 데이터 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for exchange in exchanges:
                exchange_dict = exchange.dict()
                exchange_dict['crypto_id'] = str(exchange_dict['crypto_id'])
                # Decimal을 float로 변환
                for key, value in exchange_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        exchange_dict[key] = float(value)
                data.append(exchange_dict)
            
            response = self.client.table('exchange_data')\
                .upsert(data, on_conflict='crypto_id,timestamp,exchange_name,data_source')\
                .execute()
            
            self.logger.info(f"거래소 데이터 {len(exchanges)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "거래소 데이터 삽입 실패")
            return False
    
    def insert_sentiment_metrics(self, metrics: List[SentimentMetric]) -> bool:
        """
        감성 메트릭 데이터 배치 삽입
        
        Args:
            metrics: 감성 메트릭 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for metric in metrics:
                metric_dict = metric.dict()
                metric_dict['crypto_id'] = str(metric_dict['crypto_id'])
                # Decimal을 float로 변환
                for key, value in metric_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        metric_dict[key] = float(value)
                data.append(metric_dict)
            
            response = self.client.table('sentiment_metrics')\
                .upsert(data, on_conflict='crypto_id,timestamp,data_source')\
                .execute()
            
            self.logger.info(f"감성 메트릭 {len(metrics)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "감성 메트릭 삽입 실패")
            return False
    
    def insert_derivatives_metrics(self, metrics: List[DerivativesMetric]) -> bool:
        """
        파생상품 메트릭 데이터 배치 삽입
        
        Args:
            metrics: 파생상품 메트릭 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for metric in metrics:
                metric_dict = metric.dict()
                metric_dict['crypto_id'] = str(metric_dict['crypto_id'])
                # Decimal을 float로 변환
                for key, value in metric_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        metric_dict[key] = float(value)
                data.append(metric_dict)
            
            response = self.client.table('derivatives_metrics')\
                .upsert(data, on_conflict='crypto_id,timestamp,data_source')\
                .execute()
            
            self.logger.info(f"파생상품 메트릭 {len(metrics)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "파생상품 메트릭 삽입 실패")
            return False
    
    def insert_dispersion_scores(self, scores: List[DispersionScore]) -> bool:
        """
        분산도 점수 데이터 배치 삽입
        
        Args:
            scores: 분산도 점수 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for score in scores:
                score_dict = score.dict()
                score_dict['crypto_id'] = str(score_dict['crypto_id'])
                # Decimal을 float로 변환
                for key, value in score_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        score_dict[key] = float(value)
                data.append(score_dict)
            
            response = self.client.table('dispersion_scores')\
                .upsert(data, on_conflict='crypto_id,timestamp')\
                .execute()
            
            self.logger.info(f"분산도 점수 {len(scores)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "분산도 점수 삽입 실패")
            return False
    
    def get_latest_market_metrics(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 시장 메트릭 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            시장 메트릭 리스트
        """
        try:
            response = self.client.table('market_metrics')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"시장 메트릭 조회 실패: {crypto_id}")
            return []
    
    def get_latest_price_history(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 가격 히스토리 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            가격 히스토리 리스트
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
            log_error(self.logger, e, f"가격 히스토리 조회 실패: {crypto_id}")
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
                .order('symbol')\
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
