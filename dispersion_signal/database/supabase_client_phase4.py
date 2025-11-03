"""
Supabase 클라이언트 및 데이터베이스 작업 (Phase 4)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
import logging
from supabase import create_client, Client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .models_phase4 import MultiSourcePrice, RedditSentiment, EnhancedDispersionSignal
from utils.logger import log_error

class SupabaseClientPhase4:
    """Supabase 데이터베이스 클라이언트 (Phase 4)"""
    
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
    
    def insert_multi_source_prices(self, prices: List[MultiSourcePrice]) -> bool:
        """
        다중 소스 가격 데이터 배치 삽입
        
        Args:
            prices: 다중 소스 가격 데이터 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for price in prices:
                data_dict = price.dict()
                data_dict['crypto_id'] = str(data_dict['crypto_id'])
                
                # Decimal을 float로 변환
                for key, value in data_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        data_dict[key] = float(value)
                    elif isinstance(value, datetime):
                        data_dict[key] = value.isoformat()
                
                data.append(data_dict)
            
            response = self.client.table('multi_source_prices')\
                .upsert(data, on_conflict='crypto_id,timestamp')\
                .execute()
            
            self.logger.info(f"다중 소스 가격 데이터 {len(prices)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "다중 소스 가격 데이터 삽입 실패")
            return False
    
    def insert_reddit_sentiment(self, sentiments: List[RedditSentiment]) -> bool:
        """
        Reddit 감성 데이터 배치 삽입
        
        Args:
            sentiments: Reddit 감성 데이터 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for sentiment in sentiments:
                data_dict = sentiment.dict()
                data_dict['crypto_id'] = str(data_dict['crypto_id'])
                
                # Decimal을 float로 변환
                for key, value in data_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        data_dict[key] = float(value)
                    elif isinstance(value, datetime):
                        data_dict[key] = value.isoformat()
                
                data.append(data_dict)
            
            response = self.client.table('reddit_sentiment')\
                .upsert(data, on_conflict='crypto_id,timestamp,data_source')\
                .execute()
            
            self.logger.info(f"Reddit 감성 데이터 {len(sentiments)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "Reddit 감성 데이터 삽입 실패")
            return False
    
    def insert_enhanced_dispersion_signals(self, signals: List[EnhancedDispersionSignal]) -> bool:
        """
        향상된 분산도 신호 데이터 배치 삽입
        
        Args:
            signals: 향상된 분산도 신호 데이터 리스트
        
        Returns:
            성공 여부
        """
        try:
            data = []
            for signal in signals:
                data_dict = signal.dict()
                data_dict['crypto_id'] = str(data_dict['crypto_id'])
                
                # Decimal을 float로 변환
                for key, value in data_dict.items():
                    if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                        data_dict[key] = float(value)
                    elif isinstance(value, datetime):
                        data_dict[key] = value.isoformat()
                
                data.append(data_dict)
            
            response = self.client.table('enhanced_dispersion_signals')\
                .upsert(data, on_conflict='crypto_id,timestamp')\
                .execute()
            
            self.logger.info(f"향상된 분산도 신호 데이터 {len(signals)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "향상된 분산도 신호 데이터 삽입 실패")
            return False
    
    def get_latest_multi_source_prices(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 다중 소스 가격 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            다중 소스 가격 리스트
        """
        try:
            response = self.client.table('multi_source_prices')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"다중 소스 가격 조회 실패: {crypto_id}")
            return []
    
    def get_latest_reddit_sentiment(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 Reddit 감성 데이터 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            Reddit 감성 데이터 리스트
        """
        try:
            response = self.client.table('reddit_sentiment')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"Reddit 감성 데이터 조회 실패: {crypto_id}")
            return []
    
    def get_latest_enhanced_signals(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 향상된 분산도 신호 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            향상된 분산도 신호 리스트
        """
        try:
            response = self.client.table('enhanced_dispersion_signals')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"향상된 분산도 신호 조회 실패: {crypto_id}")
            return []
    
    def get_enhanced_signals_by_level(self, signal_level: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        신호 레벨별 향상된 분산도 신호 조회
        
        Args:
            signal_level: 신호 레벨 (1-5)
            limit: 조회할 레코드 수
        
        Returns:
            향상된 분산도 신호 리스트
        """
        try:
            response = self.client.table('enhanced_dispersion_signals')\
                .select('*, cryptocurrencies(symbol, name)')\
                .eq('signal_level', signal_level)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"신호 레벨별 향상된 분산도 신호 조회 실패: {signal_level}")
            return []
    
    def get_enhanced_signals_by_type(self, signal_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        신호 타입별 향상된 분산도 신호 조회
        
        Args:
            signal_type: 신호 타입
            limit: 조회할 레코드 수
        
        Returns:
            향상된 분산도 신호 리스트
        """
        try:
            response = self.client.table('enhanced_dispersion_signals')\
                .select('*, cryptocurrencies(symbol, name)')\
                .eq('signal_type', signal_type)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"신호 타입별 향상된 분산도 신호 조회 실패: {signal_type}")
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
            
            # Phase 4 데이터 수
            multi_source_response = self.client.table('multi_source_prices')\
                .select('count')\
                .execute()
            summary['total_multi_source_prices'] = multi_source_response.data[0]['count'] if multi_source_response.data else 0
            
            reddit_response = self.client.table('reddit_sentiment')\
                .select('count')\
                .execute()
            summary['total_reddit_sentiment'] = reddit_response.data[0]['count'] if reddit_response.data else 0
            
            enhanced_response = self.client.table('enhanced_dispersion_signals')\
                .select('count')\
                .execute()
            summary['total_enhanced_signals'] = enhanced_response.data[0]['count'] if enhanced_response.data else 0
            
            # Phase 3 데이터 수
            dispersion_response = self.client.table('dispersion_signals')\
                .select('count')\
                .execute()
            summary['total_dispersion_signals'] = dispersion_response.data[0]['count'] if dispersion_response.data else 0
            
            summary_response = self.client.table('dispersion_summary_daily')\
                .select('count')\
                .execute()
            summary['total_dispersion_summaries'] = summary_response.data[0]['count'] if summary_response.data else 0
            
            # Phase 2 데이터 수
            marketcap_response = self.client.table('market_cap_data')\
                .select('count')\
                .execute()
            summary['total_marketcap_records'] = marketcap_response.data[0]['count'] if marketcap_response.data else 0
            
            global_response = self.client.table('global_metrics')\
                .select('count')\
                .execute()
            summary['total_global_records'] = global_response.data[0]['count'] if global_response.data else 0
            
            # Phase 1 데이터 수
            daily_response = self.client.table('market_data_daily')\
                .select('count')\
                .execute()
            summary['total_daily_records'] = daily_response.data[0]['count'] if daily_response.data else 0
            
            history_response = self.client.table('price_history')\
                .select('count')\
                .execute()
            summary['total_history_records'] = history_response.data[0]['count'] if history_response.data else 0
            
            return summary
            
        except Exception as e:
            log_error(self.logger, e, "데이터 요약 조회 실패")
            return {}
