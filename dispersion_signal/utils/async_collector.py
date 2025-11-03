"""
비동기 데이터 수집 및 캐싱 시스템
"""
import asyncio
import aiohttp
import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import pickle
from pathlib import Path

class CacheStrategy(Enum):
    """캐시 전략"""
    LRU = "lru"           # Least Recently Used
    TTL = "ttl"           # Time To Live
    SIZE_LIMITED = "size_limited"  # 크기 제한

@dataclass
class CacheConfig:
    """캐시 설정"""
    cache_directory: str = "cache"
    max_cache_size_mb: int = 100  # 최대 캐시 크기 (MB)
    default_ttl_seconds: int = 300  # 기본 TTL (5분)
    max_entries: int = 1000  # 최대 엔트리 수
    strategy: CacheStrategy = CacheStrategy.TTL

@dataclass
class AsyncRequestConfig:
    """비동기 요청 설정"""
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

class AsyncDataCollector:
    """비동기 데이터 수집기"""
    
    def __init__(self, config: AsyncRequestConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def fetch_data(self, url: str, headers: Optional[Dict[str, str]] = None, 
                        params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        비동기 데이터 페치
        
        Args:
            url: 요청 URL
            headers: 요청 헤더
            params: 요청 파라미터
            
        Returns:
            응답 데이터 또는 None
        """
        async with self.semaphore:
            for attempt in range(self.config.retry_attempts):
                try:
                    async with self.session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.logger.debug(f"비동기 요청 성공: {url}")
                            return data
                        elif response.status == 429:  # Rate limit
                            wait_time = 2 ** attempt
                            self.logger.warning(f"Rate limit 도달, {wait_time}초 대기: {url}")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            self.logger.warning(f"HTTP {response.status}: {url}")
                            
                except asyncio.TimeoutError:
                    self.logger.warning(f"요청 타임아웃 (시도 {attempt + 1}): {url}")
                except Exception as e:
                    self.logger.error(f"요청 실패 (시도 {attempt + 1}): {e}")
                
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
            
            self.logger.error(f"모든 재시도 실패: {url}")
            return None
    
    async def fetch_multiple(self, requests: List[Tuple[str, Optional[Dict[str, str]], Optional[Dict[str, Any]]]]) -> List[Optional[Dict[str, Any]]]:
        """
        여러 요청을 병렬로 처리
        
        Args:
            requests: (url, headers, params) 튜플 리스트
            
        Returns:
            응답 데이터 리스트
        """
        tasks = []
        for url, headers, params in requests:
            task = self.fetch_data(url, headers, params)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 처리
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"요청 {i} 실패: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results

class CacheManager:
    """캐시 관리자"""
    
    def __init__(self, config: CacheConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # 캐시 디렉토리 생성
        self.cache_path = Path(config.cache_directory)
        self.cache_path.mkdir(exist_ok=True)
        
        # 메모리 캐시
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
        
        # 캐시 통계
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_size_bytes': 0
        }
    
    def _generate_cache_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """캐시 키 생성"""
        key_data = f"{url}"
        if params:
            key_data += f"_{json.dumps(params, sort_keys=True)}"
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """캐시 엔트리 만료 여부 확인"""
        if self.config.strategy != CacheStrategy.TTL:
            return False
        
        created_at = datetime.fromisoformat(cache_entry['created_at'])
        ttl = cache_entry.get('ttl', self.config.default_ttl_seconds)
        
        return datetime.now(timezone.utc) - created_at > timedelta(seconds=ttl)
    
    def _evict_old_entries(self):
        """오래된 엔트리 제거"""
        if len(self.memory_cache) <= self.config.max_entries:
            return
        
        # LRU 전략
        if self.config.strategy == CacheStrategy.LRU:
            sorted_entries = sorted(self.access_times.items(), key=lambda x: x[1])
            entries_to_remove = len(self.memory_cache) - self.config.max_entries
            
            for key, _ in sorted_entries[:entries_to_remove]:
                self._remove_entry(key)
                self.stats['evictions'] += 1
        
        # 크기 제한 전략
        elif self.config.strategy == CacheStrategy.SIZE_LIMITED:
            max_size_bytes = self.config.max_cache_size_mb * 1024 * 1024
            
            while self.stats['total_size_bytes'] > max_size_bytes and self.memory_cache:
                # 가장 오래된 엔트리 제거
                oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
                self._remove_entry(oldest_key)
                self.stats['evictions'] += 1
    
    def _remove_entry(self, key: str):
        """캐시 엔트리 제거"""
        if key in self.memory_cache:
            entry_size = len(pickle.dumps(self.memory_cache[key]))
            self.stats['total_size_bytes'] -= entry_size
            
            del self.memory_cache[key]
            del self.access_times[key]
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        캐시에서 데이터 조회
        
        Args:
            url: 요청 URL
            params: 요청 파라미터
            
        Returns:
            캐시된 데이터 또는 None
        """
        cache_key = self._generate_cache_key(url, params)
        
        if cache_key in self.memory_cache:
            cache_entry = self.memory_cache[cache_key]
            
            # 만료 확인
            if self._is_expired(cache_entry):
                self._remove_entry(cache_key)
                self.stats['misses'] += 1
                return None
            
            # 접근 시간 업데이트
            self.access_times[cache_key] = datetime.now(timezone.utc)
            self.stats['hits'] += 1
            
            self.logger.debug(f"캐시 히트: {url}")
            return cache_entry['data']
        
        self.stats['misses'] += 1
        self.logger.debug(f"캐시 미스: {url}")
        return None
    
    def set(self, url: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None, 
            ttl: Optional[int] = None):
        """
        캐시에 데이터 저장
        
        Args:
            url: 요청 URL
            data: 저장할 데이터
            params: 요청 파라미터
            ttl: TTL (초)
        """
        cache_key = self._generate_cache_key(url, params)
        
        cache_entry = {
            'data': data,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'ttl': ttl or self.config.default_ttl_seconds,
            'url': url,
            'params': params
        }
        
        # 기존 엔트리 크기 제거
        if cache_key in self.memory_cache:
            old_size = len(pickle.dumps(self.memory_cache[cache_key]))
            self.stats['total_size_bytes'] -= old_size
        
        # 새 엔트리 저장
        entry_size = len(pickle.dumps(cache_entry))
        self.memory_cache[cache_key] = cache_entry
        self.access_times[cache_key] = datetime.now(timezone.utc)
        self.stats['total_size_bytes'] += entry_size
        
        # 캐시 크기 관리
        self._evict_old_entries()
        
        self.logger.debug(f"캐시 저장: {url}")
    
    def clear(self):
        """캐시 전체 삭제"""
        self.memory_cache.clear()
        self.access_times.clear()
        self.stats['total_size_bytes'] = 0
        self.logger.info("캐시 전체 삭제 완료")
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': round(hit_rate, 2),
            'evictions': self.stats['evictions'],
            'total_entries': len(self.memory_cache),
            'total_size_mb': round(self.stats['total_size_bytes'] / (1024 * 1024), 2),
            'max_size_mb': self.config.max_cache_size_mb,
            'strategy': self.config.strategy.value
        }

class OptimizedDataCollector:
    """최적화된 데이터 수집기 (비동기 + 캐싱)"""
    
    def __init__(self, async_config: AsyncRequestConfig, cache_config: CacheConfig, 
                 logger: Optional[logging.Logger] = None):
        self.async_collector = AsyncDataCollector(async_config, logger)
        self.cache_manager = CacheManager(cache_config, logger)
        self.logger = logger or logging.getLogger(__name__)
    
    async def collect_data_optimized(self, requests: List[Tuple[str, Optional[Dict[str, str]], Optional[Dict[str, Any]]]]) -> List[Optional[Dict[str, Any]]]:
        """
        최적화된 데이터 수집 (캐싱 + 비동기)
        
        Args:
            requests: (url, headers, params) 튜플 리스트
            
        Returns:
            데이터 리스트
        """
        # 캐시에서 먼저 확인
        cached_results = []
        uncached_requests = []
        uncached_indices = []
        
        for i, (url, headers, params) in enumerate(requests):
            cached_data = self.cache_manager.get(url, params)
            if cached_data is not None:
                cached_results.append(cached_data)
            else:
                cached_results.append(None)
                uncached_requests.append((url, headers, params))
                uncached_indices.append(i)
        
        # 캐시되지 않은 요청들을 비동기로 처리
        if uncached_requests:
            async with self.async_collector as collector:
                fresh_results = await collector.fetch_multiple(uncached_requests)
            
            # 결과를 캐시에 저장하고 원래 위치에 배치
            for i, result in enumerate(fresh_results):
                original_index = uncached_indices[i]
                url, headers, params = requests[original_index]
                
                if result is not None:
                    self.cache_manager.set(url, result, params)
                
                cached_results[original_index] = result
        
        return cached_results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        cache_stats = self.cache_manager.get_stats()
        
        return {
            'cache_stats': cache_stats,
            'async_config': {
                'max_concurrent_requests': self.async_collector.config.max_concurrent_requests,
                'request_timeout': self.async_collector.config.request_timeout,
                'retry_attempts': self.async_collector.config.retry_attempts
            }
        }
