"""
CryptoQuant API 클라이언트
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .base import BaseCollector
from utils.logger import log_error

class CryptoQuantCollector(BaseCollector):
    """CryptoQuant API 데이터 수집기"""
    
    def __init__(self, api_key: str):
        """
        CryptoQuant 수집기 초기화
        
        Args:
            api_key: CryptoQuant API 키
        """
        super().__init__(
            api_key=api_key,
            base_url='https://api.cryptoquant.com/v1',
            rate_limit=10  # 무료 플랜 제한
        )
    
    def collect_data(self, symbol: str, start_date: datetime, end_date: datetime, interval: str = '1hour') -> List[Dict[str, Any]]:
        """
        CryptoQuant에서 온체인 데이터 수집
        
        Args:
            symbol: 코인 심볼 (예: 'btc')
            start_date: 시작 날짜
            end_date: 종료 날짜
            interval: 데이터 간격
        
        Returns:
            수집된 온체인 메트릭 리스트
        """
        try:
            # 심볼을 소문자로 변환 (CryptoQuant API 요구사항)
            symbol_lower = symbol.lower()
            
            # 각 메트릭별로 데이터 수집
            metrics_data = {}
            
            # 1. 거래소 넷플로우
            exchange_netflow = self._get_exchange_netflow(symbol_lower, start_date, end_date)
            if exchange_netflow:
                metrics_data['exchange_netflow'] = exchange_netflow
            
            # 2. 거래소 잔고
            exchange_reserve = self._get_exchange_reserve(symbol_lower, start_date, end_date)
            if exchange_reserve:
                metrics_data['exchange_reserve'] = exchange_reserve
            
            # 3. 활성 주소 수
            active_addresses = self._get_active_addresses(symbol_lower, start_date, end_date)
            if active_addresses:
                metrics_data['active_addresses'] = active_addresses
            
            # 4. 채굴자 넷플로우 (Bitcoin만)
            if symbol_lower == 'btc':
                miner_netflow = self._get_miner_netflow(symbol_lower, start_date, end_date)
                if miner_netflow:
                    metrics_data['miner_netflow'] = miner_netflow
            
            # 5. 트랜잭션 수
            transaction_count = self._get_transaction_count(symbol_lower, start_date, end_date)
            if transaction_count:
                metrics_data['transaction_count'] = transaction_count
            
            # 6. 트랜잭션 볼륨
            transaction_volume = self._get_transaction_volume(symbol_lower, start_date, end_date)
            if transaction_volume:
                metrics_data['transaction_volume'] = transaction_volume
            
            # 데이터 병합
            merged_data = self._merge_metrics_data(metrics_data, symbol_lower)
            
            return merged_data
            
        except Exception as e:
            log_error(None, e, f"CryptoQuant 데이터 수집 실패: {symbol}")
            return []
    
    def _get_exchange_netflow(self, symbol: str, start_date: datetime, end_date: datetime) -> Optional[Dict[str, Any]]:
        """거래소 넷플로우 데이터 수집"""
        endpoint = f"/{symbol}/exchange-flows/netflow"
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'interval': '1h'
        }
        
        response = self._make_request(endpoint, params)
        if response and 'result' in response:
            return {
                'data': response['result']['data'],
                'endpoint': endpoint,
                'raw_response': response
            }
        return None
    
    def _get_exchange_reserve(self, symbol: str, start_date: datetime, end_date: datetime) -> Optional[Dict[str, Any]]:
        """거래소 잔고 데이터 수집"""
        endpoint = f"/{symbol}/exchange-flows/reserve"
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'interval': '1h'
        }
        
        response = self._make_request(endpoint, params)
        if response and 'result' in response:
            return {
                'data': response['result']['data'],
                'endpoint': endpoint,
                'raw_response': response
            }
        return None
    
    def _get_active_addresses(self, symbol: str, start_date: datetime, end_date: datetime) -> Optional[Dict[str, Any]]:
        """활성 주소 수 데이터 수집"""
        endpoint = f"/{symbol}/network-data/active-addresses"
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'interval': '1h'
        }
        
        response = self._make_request(endpoint, params)
        if response and 'result' in response:
            return {
                'data': response['result']['data'],
                'endpoint': endpoint,
                'raw_response': response
            }
        return None
    
    def _get_miner_netflow(self, symbol: str, start_date: datetime, end_date: datetime) -> Optional[Dict[str, Any]]:
        """채굴자 넷플로우 데이터 수집 (Bitcoin만)"""
        endpoint = f"/{symbol}/miner-flows/netflow"
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'interval': '1h'
        }
        
        response = self._make_request(endpoint, params)
        if response and 'result' in response:
            return {
                'data': response['result']['data'],
                'endpoint': endpoint,
                'raw_response': response
            }
        return None
    
    def _get_transaction_count(self, symbol: str, start_date: datetime, end_date: datetime) -> Optional[Dict[str, Any]]:
        """트랜잭션 수 데이터 수집"""
        endpoint = f"/{symbol}/network-data/transaction-count"
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'interval': '1h'
        }
        
        response = self._make_request(endpoint, params)
        if response and 'result' in response:
            return {
                'data': response['result']['data'],
                'endpoint': endpoint,
                'raw_response': response
            }
        return None
    
    def _get_transaction_volume(self, symbol: str, start_date: datetime, end_date: datetime) -> Optional[Dict[str, Any]]:
        """트랜잭션 볼륨 데이터 수집"""
        endpoint = f"/{symbol}/network-data/transaction-volume"
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'interval': '1h'
        }
        
        response = self._make_request(endpoint, params)
        if response and 'result' in response:
            return {
                'data': response['result']['data'],
                'endpoint': endpoint,
                'raw_response': response
            }
        return None
    
    def _merge_metrics_data(self, metrics_data: Dict[str, Dict[str, Any]], symbol: str) -> List[Dict[str, Any]]:
        """
        여러 메트릭 데이터를 시간별로 병합
        
        Args:
            metrics_data: 메트릭별 데이터 딕셔너리
            symbol: 코인 심볼
        
        Returns:
            병합된 데이터 리스트
        """
        # 모든 타임스탬프 수집
        all_timestamps = set()
        for metric_data in metrics_data.values():
            if 'data' in metric_data:
                for item in metric_data['data']:
                    if 'datetime' in item:
                        all_timestamps.add(item['datetime'])
        
        # 타임스탬프별로 데이터 병합
        merged_data = []
        for timestamp in sorted(all_timestamps):
            record = {
                'timestamp': timestamp,
                'symbol': symbol,
                'data_source': 'cryptoquant',
                'raw_data': {}
            }
            
            # 각 메트릭에서 해당 타임스탬프 데이터 찾기
            for metric_name, metric_data in metrics_data.items():
                if 'data' in metric_data:
                    for item in metric_data['data']:
                        if item.get('datetime') == timestamp:
                            # 메트릭별로 적절한 필드명 매핑
                            if metric_name == 'exchange_netflow':
                                record['exchange_netflow'] = item.get('value')
                            elif metric_name == 'exchange_reserve':
                                record['exchange_reserve'] = item.get('value')
                            elif metric_name == 'active_addresses':
                                record['active_addresses'] = item.get('value')
                            elif metric_name == 'miner_netflow':
                                record['miner_netflow'] = item.get('value')
                            elif metric_name == 'transaction_count':
                                record['transaction_count'] = item.get('value')
                            elif metric_name == 'transaction_volume':
                                record['transaction_volume'] = item.get('value')
                            
                            # 원본 데이터 저장
                            record['raw_data'][metric_name] = item
                            break
            
            merged_data.append(record)
        
        return merged_data
