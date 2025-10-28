"""
베이스 컬렉터 클래스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import logging
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import log_api_call, log_error

class BaseCollector(ABC):
    """데이터 수집을 위한 베이스 클래스"""
    
    def __init__(self, api_key: str, base_url: str, rate_limit: int = 10):
        """
        베이스 컬렉터 초기화
        
        Args:
            api_key: API 키
            base_url: API 베이스 URL
            rate_limit: 분당 요청 제한
        """
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.request_count = 0
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def _rate_limit_check(self):
        """Rate limit 체크 및 대기"""
        current_time = time.time()
        
        # 1분이 지났으면 카운터 리셋
        if current_time - self.last_request_time >= 60:
            self.request_count = 0
            self.last_request_time = current_time
        
        # Rate limit 초과 시 대기
        if self.request_count >= self.rate_limit:
            wait_time = 60 - (current_time - self.last_request_time)
            if wait_time > 0:
                time.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        API 요청 실행
        
        Args:
            endpoint: API 엔드포인트
            params: 요청 파라미터
            max_retries: 최대 재시도 횟수
        
        Returns:
            API 응답 데이터 또는 None
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries + 1):
            try:
                # Rate limit 체크
                self._rate_limit_check()
                
                # 요청 실행
                start_time = time.time()
                response = self.session.get(url, params=params)
                response_time = time.time() - start_time
                
                # 요청 카운터 증가
                self.request_count += 1
                
                # 로깅
                logger = logging.getLogger(__name__)
                log_api_call(logger, endpoint, response.status_code, response_time)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit exceeded
                    wait_time = 60  # 1분 대기
                    time.sleep(wait_time)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # 지수 백오프
                    time.sleep(wait_time)
                    continue
                else:
                    logger = logging.getLogger(__name__)
                    log_error(logger, e, f"API 요청 실패: {endpoint}")
                    return None
        
        return None
    
    @abstractmethod
    def collect_data(self, symbol: str, start_date: datetime, end_date: datetime, interval: str = '1hour') -> List[Dict[str, Any]]:
        """
        데이터 수집 (서브클래스에서 구현)
        
        Args:
            symbol: 코인 심볼
            start_date: 시작 날짜
            end_date: 종료 날짜
            interval: 데이터 간격
        
        Returns:
            수집된 데이터 리스트
        """
        pass
    
    def get_date_range(self, days: int = 7) -> tuple[datetime, datetime]:
        """
        날짜 범위 생성
        
        Args:
            days: 수집할 일수
        
        Returns:
            (시작 날짜, 종료 날짜) 튜플
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
