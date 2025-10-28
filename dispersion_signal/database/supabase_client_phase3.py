"""
Supabase 클라이언트 및 데이터베이스 작업 (Phase 3)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from uuid import UUID
import logging
from supabase import create_client, Client
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .models_phase3 import DispersionSignal, DispersionSummaryDaily
from utils.logger import log_error

class SupabaseClientPhase3:
    """Supabase 데이터베이스 클라이언트 (Phase 3)"""
    
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
    
    def insert_dispersion_signals(self, signals: List[DispersionSignal]) -> bool:
        """
        분산도 신호 데이터 배치 삽입
        
        Args:
            signals: 분산도 신호 데이터 리스트
        
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
            
            response = self.client.table('dispersion_signals')\
                .upsert(data, on_conflict='crypto_id,timestamp')\
                .execute()
            
            self.logger.info(f"분산도 신호 데이터 {len(signals)}개 레코드 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "분산도 신호 데이터 삽입 실패")
            return False
    
    def insert_dispersion_summary(self, summary: DispersionSummaryDaily) -> bool:
        """
        일일 분산도 요약 데이터 삽입
        
        Args:
            summary: 일일 분산도 요약 데이터
        
        Returns:
            성공 여부
        """
        try:
            data_dict = summary.dict()
            
            # Decimal을 float로 변환
            for key, value in data_dict.items():
                if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                    data_dict[key] = float(value)
                elif isinstance(value, date):
                    data_dict[key] = value.isoformat()
            
            response = self.client.table('dispersion_summary_daily')\
                .upsert([data_dict], on_conflict='date')\
                .execute()
            
            self.logger.info("일일 분산도 요약 데이터 삽입 완료")
            return True
            
        except Exception as e:
            log_error(self.logger, e, "일일 분산도 요약 데이터 삽입 실패")
            return False
    
    def get_latest_dispersion_signals(self, crypto_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 분산도 신호 조회
        
        Args:
            crypto_id: 코인 ID
            limit: 조회할 레코드 수
        
        Returns:
            분산도 신호 리스트
        """
        try:
            response = self.client.table('dispersion_signals')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"분산도 신호 조회 실패: {crypto_id}")
            return []
    
    def get_dispersion_signals_by_level(self, signal_level: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        신호 레벨별 분산도 신호 조회
        
        Args:
            signal_level: 신호 레벨 (1-5)
            limit: 조회할 레코드 수
        
        Returns:
            분산도 신호 리스트
        """
        try:
            response = self.client.table('dispersion_signals')\
                .select('*, cryptocurrencies(symbol, name)')\
                .eq('signal_level', signal_level)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"신호 레벨별 분산도 신호 조회 실패: {signal_level}")
            return []
    
    def get_dispersion_signals_by_type(self, signal_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        신호 타입별 분산도 신호 조회
        
        Args:
            signal_type: 신호 타입 ('convergence', 'divergence', 'neutral')
            limit: 조회할 레코드 수
        
        Returns:
            분산도 신호 리스트
        """
        try:
            response = self.client.table('dispersion_signals')\
                .select('*, cryptocurrencies(symbol, name)')\
                .eq('signal_type', signal_type)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, f"신호 타입별 분산도 신호 조회 실패: {signal_type}")
            return []
    
    def get_latest_dispersion_summary(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 일일 분산도 요약 조회
        
        Args:
            limit: 조회할 레코드 수
        
        Returns:
            일일 분산도 요약 리스트
        """
        try:
            response = self.client.table('dispersion_summary_daily')\
                .select('*')\
                .order('date', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            log_error(self.logger, e, "일일 분산도 요약 조회 실패")
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
    
    def get_latest_market_data(self, crypto_id: UUID) -> Optional[Dict[str, Any]]:
        """
        최신 시장 데이터 조회 (Binance)
        
        Args:
            crypto_id: 코인 ID
        
        Returns:
            시장 데이터 또는 None
        """
        try:
            response = self.client.table('market_data_daily')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('date', desc=True)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            log_error(self.logger, e, f"최신 시장 데이터 조회 실패: {crypto_id}")
            return None
    
    def get_latest_market_cap_data(self, crypto_id: UUID) -> Optional[Dict[str, Any]]:
        """
        최신 시가총액 데이터 조회 (CoinMarketCap)
        
        Args:
            crypto_id: 코인 ID
        
        Returns:
            시가총액 데이터 또는 None
        """
        try:
            response = self.client.table('market_cap_data')\
                .select('*')\
                .eq('crypto_id', str(crypto_id))\
                .order('timestamp', desc=True)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            log_error(self.logger, e, f"최신 시가총액 데이터 조회 실패: {crypto_id}")
            return None
    
    def get_latest_global_metrics(self) -> Optional[Dict[str, Any]]:
        """
        최신 글로벌 메트릭 조회
        
        Returns:
            글로벌 메트릭 또는 None
        """
        try:
            response = self.client.table('global_metrics')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(1)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            log_error(self.logger, e, "최신 글로벌 메트릭 조회 실패")
            return None
    
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
            
            # 분산도 신호 수
            signals_response = self.client.table('dispersion_signals')\
                .select('count')\
                .execute()
            summary['total_dispersion_signals'] = signals_response.data[0]['count'] if signals_response.data else 0
            
            # 일일 요약 수
            summary_response = self.client.table('dispersion_summary_daily')\
                .select('count')\
                .execute()
            summary['total_dispersion_summaries'] = summary_response.data[0]['count'] if summary_response.data else 0
            
            # Phase 1 데이터 수
            daily_response = self.client.table('market_data_daily')\
                .select('count')\
                .execute()
            summary['total_daily_records'] = daily_response.data[0]['count'] if daily_response.data else 0
            
            history_response = self.client.table('price_history')\
                .select('count')\
                .execute()
            summary['total_history_records'] = history_response.data[0]['count'] if history_response.data else 0
            
            # Phase 2 데이터 수
            marketcap_response = self.client.table('market_cap_data')\
                .select('count')\
                .execute()
            summary['total_marketcap_records'] = marketcap_response.data[0]['count'] if marketcap_response.data else 0
            
            global_response = self.client.table('global_metrics')\
                .select('count')\
                .execute()
            summary['total_global_records'] = global_response.data[0]['count'] if global_response.data else 0
            
            return summary
            
        except Exception as e:
            log_error(self.logger, e, "데이터 요약 조회 실패")
            return {}
