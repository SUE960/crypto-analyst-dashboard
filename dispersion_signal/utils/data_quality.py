"""
데이터 품질 검증 및 이상치 탐지 모듈
"""
import logging
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
import statistics
import numpy as np
from datetime import datetime, timezone

class DataQualityValidator:
    """데이터 품질 검증 및 이상치 탐지 클래스"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        
        # 가격 데이터 검증 임계값
        self.price_thresholds = {
            'min_price': Decimal('0.000001'),  # 최소 가격 (1 satoshi)
            'max_price': Decimal('1000000'),    # 최대 가격 (1M USD)
            'max_deviation': Decimal('0.1'),    # 최대 편차 (10%)
            'min_sources': 1                   # 최소 소스 수 (Binance 또는 CoinGecko 중 하나만 있어도 OK)
        }
        
        # 감성 점수 검증 임계값
        self.sentiment_thresholds = {
            'min_score': Decimal('-100'),
            'max_score': Decimal('100'),
            'min_mentions': 1
        }
    
    def validate_price_data(self, prices: Dict[str, Decimal], symbol: str) -> Tuple[bool, List[str]]:
        """
        가격 데이터 품질 검증
        
        Args:
            prices: 소스별 가격 데이터 {'source': price}
            symbol: 코인 심볼
            
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # 1. 기본 범위 검증
        for source, price in prices.items():
            if price < self.price_thresholds['min_price']:
                errors.append(f"{symbol} {source} 가격이 너무 낮음: {price}")
            elif price > self.price_thresholds['max_price']:
                errors.append(f"{symbol} {source} 가격이 너무 높음: {price}")
        
        # 2. 소스 수 검증
        if len(prices) < self.price_thresholds['min_sources']:
            errors.append(f"{symbol} 가격 소스 부족: {len(prices)}개 (최소 {self.price_thresholds['min_sources']}개 필요)")
            return False, errors
        
        # 3. 소스 간 일관성 검증
        if len(prices) >= 2:
            price_values = list(prices.values())
            avg_price = sum(price_values) / len(price_values)
            
            for source, price in prices.items():
                deviation = abs(price - avg_price) / avg_price
                if deviation > self.price_thresholds['max_deviation']:
                    errors.append(f"{symbol} {source} 가격 편차 초과: {deviation:.2%} (임계값: {self.price_thresholds['max_deviation']:.2%})")
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            self.logger.warning(f"가격 데이터 품질 검증 실패 - {symbol}: {errors}")
        else:
            self.logger.debug(f"가격 데이터 품질 검증 통과 - {symbol}")
        
        return is_valid, errors
    
    def detect_price_outliers(self, prices: List[Decimal], method: str = 'iqr') -> List[int]:
        """
        가격 이상치 탐지
        
        Args:
            prices: 가격 리스트
            method: 탐지 방법 ('iqr', 'zscore', 'modified_zscore')
            
        Returns:
            이상치 인덱스 리스트
        """
        if len(prices) < 3:
            return []
        
        outlier_indices = []
        
        try:
            if method == 'iqr':
                outlier_indices = self._detect_outliers_iqr(prices)
            elif method == 'zscore':
                outlier_indices = self._detect_outliers_zscore(prices)
            elif method == 'modified_zscore':
                outlier_indices = self._detect_outliers_modified_zscore(prices)
            else:
                self.logger.warning(f"알 수 없는 이상치 탐지 방법: {method}")
                
        except Exception as e:
            self.logger.error(f"이상치 탐지 중 오류 발생: {e}")
        
        return outlier_indices
    
    def _detect_outliers_iqr(self, prices: List[Decimal]) -> List[int]:
        """IQR 방법으로 이상치 탐지"""
        try:
            # Decimal을 float로 변환
            price_values = [float(p) for p in prices]
            
            q1 = np.percentile(price_values, 25)
            q3 = np.percentile(price_values, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outlier_indices = []
            for i, price in enumerate(price_values):
                if price < lower_bound or price > upper_bound:
                    outlier_indices.append(i)
            
            return outlier_indices
            
        except Exception as e:
            self.logger.error(f"IQR 이상치 탐지 실패: {e}")
            return []
    
    def _detect_outliers_zscore(self, prices: List[Decimal]) -> List[int]:
        """Z-score 방법으로 이상치 탐지 (임계값: 3)"""
        try:
            price_values = [float(p) for p in prices]
            mean_price = statistics.mean(price_values)
            std_price = statistics.stdev(price_values)
            
            if std_price == 0:
                return []
            
            outlier_indices = []
            for i, price in enumerate(price_values):
                z_score = abs((price - mean_price) / std_price)
                if z_score > 3:
                    outlier_indices.append(i)
            
            return outlier_indices
            
        except Exception as e:
            self.logger.error(f"Z-score 이상치 탐지 실패: {e}")
            return []
    
    def _detect_outliers_modified_zscore(self, prices: List[Decimal]) -> List[int]:
        """Modified Z-score 방법으로 이상치 탐지 (임계값: 3.5)"""
        try:
            price_values = [float(p) for p in prices]
            median_price = statistics.median(price_values)
            
            # Median Absolute Deviation 계산
            mad_values = [abs(price - median_price) for price in price_values]
            mad = statistics.median(mad_values)
            
            if mad == 0:
                return []
            
            outlier_indices = []
            for i, price in enumerate(price_values):
                modified_z_score = 0.6745 * (price - median_price) / mad
                if abs(modified_z_score) > 3.5:
                    outlier_indices.append(i)
            
            return outlier_indices
            
        except Exception as e:
            self.logger.error(f"Modified Z-score 이상치 탐지 실패: {e}")
            return []
    
    def validate_sentiment_data(self, sentiment_score: Decimal, mention_count: int, symbol: str) -> Tuple[bool, List[str]]:
        """
        감성 데이터 품질 검증
        
        Args:
            sentiment_score: 감성 점수 (-100 ~ 100)
            mention_count: 언급 수
            symbol: 코인 심볼
            
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # 감성 점수 범위 검증
        if sentiment_score < self.sentiment_thresholds['min_score'] or sentiment_score > self.sentiment_thresholds['max_score']:
            errors.append(f"{symbol} 감성 점수 범위 초과: {sentiment_score}")
        
        # 언급 수 검증
        if mention_count < self.sentiment_thresholds['min_mentions']:
            errors.append(f"{symbol} 언급 수 부족: {mention_count}")
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            self.logger.warning(f"감성 데이터 품질 검증 실패 - {symbol}: {errors}")
        else:
            self.logger.debug(f"감성 데이터 품질 검증 통과 - {symbol}")
        
        return is_valid, errors
    
    def validate_timestamp(self, timestamp: datetime) -> Tuple[bool, str]:
        """
        타임스탬프 검증
        
        Args:
            timestamp: 검증할 타임스탬프
            
        Returns:
            (is_valid, error_message)
        """
        now = datetime.now(timezone.utc)
        
        # 미래 시간 검증
        if timestamp > now:
            return False, f"미래 시간: {timestamp}"
        
        # 너무 오래된 시간 검증 (1년 이상)
        one_year_ago = now.replace(year=now.year - 1)
        if timestamp < one_year_ago:
            return False, f"너무 오래된 시간: {timestamp}"
        
        # 타임존 검증
        if timestamp.tzinfo is None:
            return False, "타임존 정보 없음"
        
        return True, ""
    
    def get_data_quality_score(self, prices: Dict[str, Decimal], sentiment_score: Optional[Decimal] = None) -> float:
        """
        데이터 품질 점수 계산 (0-100)
        
        Args:
            prices: 가격 데이터
            sentiment_score: 감성 점수 (선택사항)
            
        Returns:
            품질 점수 (0-100)
        """
        score = 0.0
        
        # 가격 데이터 품질 (70점 만점)
        if len(prices) >= 2:
            price_values = list(prices.values())
            avg_price = sum(price_values) / len(price_values)
            
            # 소스 수 점수 (20점)
            source_score = min(20, len(prices) * 4)
            
            # 일관성 점수 (50점)
            consistency_score = 50
            for price in price_values:
                deviation = abs(price - avg_price) / avg_price
                if deviation > self.price_thresholds['max_deviation']:
                    consistency_score -= deviation * 100
            
            consistency_score = max(0, consistency_score)
            score += source_score + consistency_score
        
        # 감성 데이터 품질 (30점 만점)
        if sentiment_score is not None:
            if self.sentiment_thresholds['min_score'] <= sentiment_score <= self.sentiment_thresholds['max_score']:
                score += 30
        
        return min(100.0, score)
    
    def generate_quality_report(self, symbol: str, prices: Dict[str, Decimal], 
                              sentiment_score: Optional[Decimal] = None) -> Dict[str, Any]:
        """
        데이터 품질 리포트 생성
        
        Args:
            symbol: 코인 심볼
            prices: 가격 데이터
            sentiment_score: 감성 점수
            
        Returns:
            품질 리포트 딕셔너리
        """
        report = {
            'symbol': symbol,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'price_validation': {},
            'sentiment_validation': {},
            'quality_score': 0.0,
            'recommendations': []
        }
        
        # 가격 데이터 검증
        price_valid, price_errors = self.validate_price_data(prices, symbol)
        report['price_validation'] = {
            'is_valid': price_valid,
            'errors': price_errors,
            'source_count': len(prices),
            'outliers': []
        }
        
        # 이상치 탐지
        if len(prices) >= 3:
            price_values = list(prices.values())
            outlier_indices = self.detect_price_outliers(price_values)
            if outlier_indices:
                outlier_sources = [list(prices.keys())[i] for i in outlier_indices]
                report['price_validation']['outliers'] = outlier_sources
        
        # 감성 데이터 검증
        if sentiment_score is not None:
            sentiment_valid, sentiment_errors = self.validate_sentiment_data(sentiment_score, 1, symbol)
            report['sentiment_validation'] = {
                'is_valid': sentiment_valid,
                'errors': sentiment_errors,
                'score': float(sentiment_score)
            }
        
        # 품질 점수 계산
        report['quality_score'] = self.get_data_quality_score(prices, sentiment_score)
        
        # 권장사항 생성
        if not price_valid:
            report['recommendations'].append("가격 데이터 소스 추가 또는 이상치 제거 필요")
        if sentiment_score is not None and not report['sentiment_validation'].get('is_valid', True):
            report['recommendations'].append("감성 데이터 품질 개선 필요")
        if report['quality_score'] < 70:
            report['recommendations'].append("전반적인 데이터 품질 개선 필요")
        
        return report
