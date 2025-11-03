"""
분석가 목표가 데이터 품질 검증 및 중복 제거 모듈
수집된 데이터의 품질을 검증하고 중복을 제거하는 기능을 제공
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import re
from collections import defaultdict

from database.models_analyst_targets import (
    AnalystProfile, AnalystTarget, MarketInsight, SentimentAnalysis,
    MarketIndex, SectorAnalysis, CollectedAnalystData
)
from utils.logger import log_info, log_error

logger = logging.getLogger(__name__)

class DataQualityValidator:
    """데이터 품질 검증 클래스"""
    
    def __init__(self):
        """검증기 초기화"""
        # 가격 목표가 검증 기준
        self.price_thresholds = {
            'min_price': Decimal('0.000001'),  # 최소 가격 (1 satoshi)
            'max_price': Decimal('10000000'),   # 최대 가격 (10M USD)
            'max_price_change': Decimal('1000'), # 최대 가격 변화율 (1000%)
            'min_price_change': Decimal('-90'),  # 최소 가격 변화율 (-90%)
            'min_confidence': 1,                 # 최소 신뢰도
            'max_confidence': 10,                # 최대 신뢰도
            'max_timeframe_months': 60,         # 최대 시간대 (5년)
            'min_timeframe_months': 1            # 최소 시간대 (1개월)
        }
        
        # 분석가 프로필 검증 기준
        self.profile_thresholds = {
            'min_name_length': 2,               # 최소 이름 길이
            'max_name_length': 100,             # 최대 이름 길이
            'min_reliability': 0,               # 최소 신뢰도
            'max_reliability': 100,             # 최대 신뢰도
            'min_accuracy': 0,                  # 최소 정확도
            'max_accuracy': 100,                # 최대 정확도
            'max_followers': 10000000,          # 최대 팔로워 수
            'min_followers': 0                   # 최소 팔로워 수
        }
        
        # 인사이트 검증 기준
        self.insight_thresholds = {
            'min_content_length': 10,           # 최소 내용 길이
            'max_content_length': 10000,        # 최대 내용 길이
            'min_confidence': 1,                 # 최소 신뢰도
            'max_confidence': 10                 # 최대 신뢰도
        }
    
    def validate_price_target(self, target: AnalystTarget) -> Tuple[bool, List[str]]:
        """
        가격 목표가 검증
        
        Args:
            target: 분석가 목표가 모델
        
        Returns:
            (유효성 여부, 오류 메시지 리스트)
        """
        errors = []
        
        try:
            # 가격 범위 검증
            if target.current_price <= 0:
                errors.append(f"현재 가격이 0 이하입니다: {target.current_price}")
            elif target.current_price < self.price_thresholds['min_price']:
                errors.append(f"현재 가격이 너무 낮습니다: {target.current_price}")
            elif target.current_price > self.price_thresholds['max_price']:
                errors.append(f"현재 가격이 너무 높습니다: {target.current_price}")
            
            if target.target_price <= 0:
                errors.append(f"목표 가격이 0 이하입니다: {target.target_price}")
            elif target.target_price < self.price_thresholds['min_price']:
                errors.append(f"목표 가격이 너무 낮습니다: {target.target_price}")
            elif target.target_price > self.price_thresholds['max_price']:
                errors.append(f"목표 가격이 너무 높습니다: {target.target_price}")
            
            # 가격 변화율 검증
            if target.price_change_percent:
                if target.price_change_percent < self.price_thresholds['min_price_change']:
                    errors.append(f"가격 변화율이 너무 낮습니다: {target.price_change_percent}%")
                elif target.price_change_percent > self.price_thresholds['max_price_change']:
                    errors.append(f"가격 변화율이 너무 높습니다: {target.price_change_percent}%")
            
            # 신뢰도 검증
            if target.confidence_level < self.price_thresholds['min_confidence']:
                errors.append(f"신뢰도가 너무 낮습니다: {target.confidence_level}")
            elif target.confidence_level > self.price_thresholds['max_confidence']:
                errors.append(f"신뢰도가 너무 높습니다: {target.confidence_level}")
            
            # 시간대 검증
            if target.timeframe_months:
                if target.timeframe_months < self.price_thresholds['min_timeframe_months']:
                    errors.append(f"시간대가 너무 짧습니다: {target.timeframe_months}개월")
                elif target.timeframe_months > self.price_thresholds['max_timeframe_months']:
                    errors.append(f"시간대가 너무 깁니다: {target.timeframe_months}개월")
            
            # 심볼 검증
            if not target.symbol or len(target.symbol.strip()) == 0:
                errors.append("코인 심볼이 비어있습니다")
            elif not re.match(r'^[A-Z0-9]{1,10}$', target.symbol):
                errors.append(f"코인 심볼 형식이 잘못되었습니다: {target.symbol}")
            
            # 분석 근거 검증
            if target.reasoning and len(target.reasoning.strip()) < 5:
                errors.append("분석 근거가 너무 짧습니다")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            log_error(logger, e, f"가격 목표가 검증 중 오류: {target.symbol}")
            return False, [f"검증 중 오류 발생: {str(e)}"]
    
    def validate_analyst_profile(self, profile: AnalystProfile) -> Tuple[bool, List[str]]:
        """
        분석가 프로필 검증
        
        Args:
            profile: 분석가 프로필 모델
        
        Returns:
            (유효성 여부, 오류 메시지 리스트)
        """
        errors = []
        
        try:
            # 이름 검증
            if not profile.name or len(profile.name.strip()) < self.profile_thresholds['min_name_length']:
                errors.append(f"분석가 이름이 너무 짧습니다: {profile.name}")
            elif len(profile.name) > self.profile_thresholds['max_name_length']:
                errors.append(f"분석가 이름이 너무 깁니다: {profile.name}")
            
            # 소스 검증
            if not profile.source or len(profile.source.strip()) == 0:
                errors.append("데이터 소스가 비어있습니다")
            
            # 신뢰도 검증
            if profile.reliability_score < self.profile_thresholds['min_reliability']:
                errors.append(f"신뢰도 점수가 너무 낮습니다: {profile.reliability_score}")
            elif profile.reliability_score > self.profile_thresholds['max_reliability']:
                errors.append(f"신뢰도 점수가 너무 높습니다: {profile.reliability_score}")
            
            # 정확도 검증
            if profile.accuracy_score < self.profile_thresholds['min_accuracy']:
                errors.append(f"정확도 점수가 너무 낮습니다: {profile.accuracy_score}")
            elif profile.accuracy_score > self.profile_thresholds['max_accuracy']:
                errors.append(f"정확도 점수가 너무 높습니다: {profile.accuracy_score}")
            
            # 팔로워 수 검증
            if profile.followers_count < self.profile_thresholds['min_followers']:
                errors.append(f"팔로워 수가 음수입니다: {profile.followers_count}")
            elif profile.followers_count > self.profile_thresholds['max_followers']:
                errors.append(f"팔로워 수가 비현실적으로 큽니다: {profile.followers_count}")
            
            # 전문 분야 검증
            if profile.expertise_areas:
                valid_areas = ['technical', 'fundamental', 'sentiment', 'mixed']
                for area in profile.expertise_areas:
                    if area not in valid_areas:
                        errors.append(f"유효하지 않은 전문 분야입니다: {area}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            log_error(logger, e, f"분석가 프로필 검증 중 오류: {profile.name}")
            return False, [f"검증 중 오류 발생: {str(e)}"]
    
    def validate_market_insight(self, insight: MarketInsight) -> Tuple[bool, List[str]]:
        """
        시장 인사이트 검증
        
        Args:
            insight: 시장 인사이트 모델
        
        Returns:
            (유효성 여부, 오류 메시지 리스트)
        """
        errors = []
        
        try:
            # 내용 길이 검증
            if not insight.content or len(insight.content.strip()) < self.insight_thresholds['min_content_length']:
                errors.append(f"인사이트 내용이 너무 짧습니다: {len(insight.content or '')}자")
            elif len(insight.content) > self.insight_thresholds['max_content_length']:
                errors.append(f"인사이트 내용이 너무 깁니다: {len(insight.content)}자")
            
            # 신뢰도 검증
            if insight.confidence < self.insight_thresholds['min_confidence']:
                errors.append(f"신뢰도가 너무 낮습니다: {insight.confidence}")
            elif insight.confidence > self.insight_thresholds['max_confidence']:
                errors.append(f"신뢰도가 너무 높습니다: {insight.confidence}")
            
            # 심볼 검증
            if not insight.symbol or len(insight.symbol.strip()) == 0:
                errors.append("코인 심볼이 비어있습니다")
            
            # 소스 검증
            if not insight.source or len(insight.source.strip()) == 0:
                errors.append("데이터 소스가 비어있습니다")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            log_error(logger, e, f"시장 인사이트 검증 중 오류: {insight.symbol}")
            return False, [f"검증 중 오류 발생: {str(e)}"]

class DuplicateDetector:
    """중복 데이터 탐지 클래스"""
    
    def __init__(self):
        """중복 탐지기 초기화"""
        self.similarity_threshold = 0.8  # 유사도 임계값
    
    def generate_target_hash(self, target: AnalystTarget) -> str:
        """
        목표가 데이터의 해시 생성
        
        Args:
            target: 분석가 목표가 모델
        
        Returns:
            해시 문자열
        """
        # 중복 판단을 위한 핵심 필드들
        key_fields = [
            target.symbol,
            str(target.target_price),
            target.timeframe,
            str(target.timeframe_months),
            target.analysis_type,
            target.source
        ]
        
        # 해시 생성
        content = '|'.join(str(field) for field in key_fields)
        return hashlib.md5(content.encode()).hexdigest()
    
    def generate_profile_hash(self, profile: AnalystProfile) -> str:
        """
        프로필 데이터의 해시 생성
        
        Args:
            profile: 분석가 프로필 모델
        
        Returns:
            해시 문자열
        """
        # 중복 판단을 위한 핵심 필드들
        key_fields = [
            profile.name,
            profile.source,
            profile.source_id
        ]
        
        # 해시 생성
        content = '|'.join(str(field) for field in key_fields)
        return hashlib.md5(content.encode()).hexdigest()
    
    def detect_duplicate_targets(self, targets: List[AnalystTarget]) -> List[Tuple[int, int]]:
        """
        중복 목표가 탐지
        
        Args:
            targets: 목표가 리스트
        
        Returns:
            중복 쌍의 인덱스 리스트
        """
        duplicates = []
        hash_map = {}
        
        for i, target in enumerate(targets):
            target_hash = self.generate_target_hash(target)
            
            if target_hash in hash_map:
                # 중복 발견
                original_index = hash_map[target_hash]
                duplicates.append((original_index, i))
            else:
                hash_map[target_hash] = i
        
        return duplicates
    
    def detect_duplicate_profiles(self, profiles: List[AnalystProfile]) -> List[Tuple[int, int]]:
        """
        중복 프로필 탐지
        
        Args:
            profiles: 프로필 리스트
        
        Returns:
            중복 쌍의 인덱스 리스트
        """
        duplicates = []
        hash_map = {}
        
        for i, profile in enumerate(profiles):
            profile_hash = self.generate_profile_hash(profile)
            
            if target_hash in hash_map:
                # 중복 발견
                original_index = hash_map[profile_hash]
                duplicates.append((original_index, i))
            else:
                hash_map[profile_hash] = i
        
        return duplicates
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        텍스트 유사도 계산 (간단한 Jaccard 유사도)
        
        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트
        
        Returns:
            유사도 (0.0 ~ 1.0)
        """
        if not text1 or not text2:
            return 0.0
        
        # 단어 집합으로 변환
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Jaccard 유사도 계산
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

class DataQualityManager:
    """데이터 품질 관리 클래스"""
    
    def __init__(self):
        """품질 관리자 초기화"""
        self.validator = DataQualityValidator()
        self.duplicate_detector = DuplicateDetector()
    
    def validate_and_clean_data(self, data: CollectedAnalystData) -> CollectedAnalystData:
        """
        데이터 검증 및 정리
        
        Args:
            data: 수집된 데이터
        
        Returns:
            정리된 데이터
        """
        cleaned_data = CollectedAnalystData()
        
        log_info(logger, "데이터 품질 검증 및 정리 시작")
        
        # 분석가 프로필 검증 및 중복 제거
        cleaned_profiles = self._clean_analyst_profiles(data.analyst_profiles)
        cleaned_data.analyst_profiles = cleaned_profiles
        
        # 분석가 목표가 검증 및 중복 제거
        cleaned_targets = self._clean_analyst_targets(data.analyst_targets)
        cleaned_data.analyst_targets = cleaned_targets
        
        # 시장 인사이트 검증 및 중복 제거
        cleaned_insights = self._clean_market_insights(data.market_insights)
        cleaned_data.market_insights = cleaned_insights
        
        # 감성 분석 검증
        cleaned_sentiment = self._clean_sentiment_analysis(data.sentiment_analysis)
        cleaned_data.sentiment_analysis = cleaned_sentiment
        
        # 시장 지수 검증
        cleaned_indices = self._clean_market_indices(data.market_indices)
        cleaned_data.market_indices = cleaned_indices
        
        # 섹터 분석 검증
        cleaned_sectors = self._clean_sector_analysis(data.sector_analysis)
        cleaned_data.sector_analysis = cleaned_sectors
        
        log_info(logger, f"데이터 정리 완료: {cleaned_data.total_records}개 레코드")
        
        return cleaned_data
    
    def _clean_analyst_profiles(self, profiles: List[AnalystProfile]) -> List[AnalystProfile]:
        """분석가 프로필 정리"""
        cleaned_profiles = []
        duplicate_indices = self.duplicate_detector.detect_duplicate_profiles(profiles)
        duplicate_set = set()
        
        for original, duplicate in duplicate_indices:
            duplicate_set.add(duplicate)
        
        for i, profile in enumerate(profiles):
            if i in duplicate_set:
                continue  # 중복 제거
            
            is_valid, errors = self.validator.validate_analyst_profile(profile)
            if is_valid:
                cleaned_profiles.append(profile)
            else:
                log_error(logger, None, f"분석가 프로필 검증 실패: {profile.name} - {errors}")
        
        log_info(logger, f"분석가 프로필 정리: {len(profiles)} → {len(cleaned_profiles)}")
        return cleaned_profiles
    
    def _clean_analyst_targets(self, targets: List[AnalystTarget]) -> List[AnalystTarget]:
        """분석가 목표가 정리"""
        cleaned_targets = []
        duplicate_indices = self.duplicate_detector.detect_duplicate_targets(targets)
        duplicate_set = set()
        
        for original, duplicate in duplicate_indices:
            duplicate_set.add(duplicate)
        
        for i, target in enumerate(targets):
            if i in duplicate_set:
                continue  # 중복 제거
            
            is_valid, errors = self.validator.validate_price_target(target)
            if is_valid:
                cleaned_targets.append(target)
            else:
                log_error(logger, None, f"가격 목표가 검증 실패: {target.symbol} - {errors}")
        
        log_info(logger, f"분석가 목표가 정리: {len(targets)} → {len(cleaned_targets)}")
        return cleaned_targets
    
    def _clean_market_insights(self, insights: List[MarketInsight]) -> List[MarketInsight]:
        """시장 인사이트 정리"""
        cleaned_insights = []
        
        for insight in insights:
            is_valid, errors = self.validator.validate_market_insight(insight)
            if is_valid:
                cleaned_insights.append(insight)
            else:
                log_error(logger, None, f"시장 인사이트 검증 실패: {insight.symbol} - {errors}")
        
        log_info(logger, f"시장 인사이트 정리: {len(insights)} → {len(cleaned_insights)}")
        return cleaned_insights
    
    def _clean_sentiment_analysis(self, sentiment_list: List[SentimentAnalysis]) -> List[SentimentAnalysis]:
        """감성 분석 정리"""
        cleaned_sentiment = []
        
        for sentiment in sentiment_list:
            # 기본적인 검증
            if (sentiment.sentiment_score >= -1 and sentiment.sentiment_score <= 1 and
                sentiment.confidence >= 0 and sentiment.confidence <= 1 and
                sentiment.total_articles > 0):
                cleaned_sentiment.append(sentiment)
            else:
                log_error(logger, None, f"감성 분석 검증 실패: {sentiment.symbol}")
        
        log_info(logger, f"감성 분석 정리: {len(sentiment_list)} → {len(cleaned_sentiment)}")
        return cleaned_sentiment
    
    def _clean_market_indices(self, indices: List[MarketIndex]) -> List[MarketIndex]:
        """시장 지수 정리"""
        cleaned_indices = []
        
        for index in indices:
            # 기본적인 검증
            if (index.value > 0 and 
                index.name and len(index.name.strip()) > 0):
                cleaned_indices.append(index)
            else:
                log_error(logger, None, f"시장 지수 검증 실패: {index.name}")
        
        log_info(logger, f"시장 지수 정리: {len(indices)} → {len(cleaned_indices)}")
        return cleaned_indices
    
    def _clean_sector_analysis(self, sectors: List[SectorAnalysis]) -> List[SectorAnalysis]:
        """섹터 분석 정리"""
        cleaned_sectors = []
        
        for sector in sectors:
            # 기본적인 검증
            if (sector.value >= 0 and 
                sector.percentage >= 0 and sector.percentage <= 100 and
                sector.metric and len(sector.metric.strip()) > 0):
                cleaned_sectors.append(sector)
            else:
                log_error(logger, None, f"섹터 분석 검증 실패: {sector.metric}")
        
        log_info(logger, f"섹터 분석 정리: {len(sectors)} → {len(cleaned_sectors)}")
        return cleaned_sectors
    
    def generate_quality_report(self, original_data: CollectedAnalystData, 
                              cleaned_data: CollectedAnalystData) -> Dict[str, Any]:
        """
        데이터 품질 보고서 생성
        
        Args:
            original_data: 원본 데이터
            cleaned_data: 정리된 데이터
        
        Returns:
            품질 보고서
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'original_counts': {
                'analyst_profiles': len(original_data.analyst_profiles),
                'analyst_targets': len(original_data.analyst_targets),
                'market_insights': len(original_data.market_insights),
                'sentiment_analysis': len(original_data.sentiment_analysis),
                'market_indices': len(original_data.market_indices),
                'sector_analysis': len(original_data.sector_analysis),
                'total': original_data.total_records
            },
            'cleaned_counts': {
                'analyst_profiles': len(cleaned_data.analyst_profiles),
                'analyst_targets': len(cleaned_data.analyst_targets),
                'market_insights': len(cleaned_data.market_insights),
                'sentiment_analysis': len(cleaned_data.sentiment_analysis),
                'market_indices': len(cleaned_data.market_indices),
                'sector_analysis': len(cleaned_data.sector_analysis),
                'total': cleaned_data.total_records
            },
            'quality_metrics': {}
        }
        
        # 품질 지표 계산
        for key in report['original_counts']:
            original = report['original_counts'][key]
            cleaned = report['cleaned_counts'][key]
            
            if original > 0:
                quality_score = (cleaned / original) * 100
                report['quality_metrics'][key] = {
                    'quality_score': round(quality_score, 2),
                    'removed_count': original - cleaned,
                    'removal_rate': round(((original - cleaned) / original) * 100, 2)
                }
        
        return report

# 테스트 함수
def test_data_quality_manager():
    """데이터 품질 관리자 테스트"""
    from database.models_analyst_targets import CollectedAnalystData, AnalystTarget, AnalystProfile
    
    print("=== 데이터 품질 관리자 테스트 ===")
    
    # 테스트 데이터 생성
    test_profile = AnalystProfile(
        name="Test Analyst",
        source="test",
        source_id="test_001",
        reliability_score=85.0
    )
    
    test_target = AnalystTarget(
        symbol="BTC",
        current_price=Decimal("50000"),
        target_price=Decimal("60000"),
        timeframe="medium_term",
        timeframe_months=6,
        analysis_type="technical",
        confidence_level=8,
        reasoning="테스트 목표가"
    )
    
    # 중복 테스트를 위한 동일한 데이터
    duplicate_target = AnalystTarget(
        symbol="BTC",
        current_price=Decimal("50000"),
        target_price=Decimal("60000"),
        timeframe="medium_term",
        timeframe_months=6,
        analysis_type="technical",
        confidence_level=8,
        reasoning="테스트 목표가"
    )
    
    # 잘못된 데이터
    invalid_target = AnalystTarget(
        symbol="",  # 빈 심볼
        current_price=Decimal("-1000"),  # 음수 가격
        target_price=Decimal("0"),  # 0 가격
        timeframe="medium_term",
        timeframe_months=6,
        analysis_type="technical",
        confidence_level=15,  # 잘못된 신뢰도
        reasoning="잘못된 데이터"
    )
    
    # 테스트 데이터 구성
    test_data = CollectedAnalystData()
    test_data.analyst_profiles = [test_profile]
    test_data.analyst_targets = [test_target, duplicate_target, invalid_target]
    
    # 품질 관리자 테스트
    quality_manager = DataQualityManager()
    cleaned_data = quality_manager.validate_and_clean_data(test_data)
    
    # 결과 확인
    print(f"원본 목표가 수: {len(test_data.analyst_targets)}")
    print(f"정리된 목표가 수: {len(cleaned_data.analyst_targets)}")
    print(f"원본 프로필 수: {len(test_data.analyst_profiles)}")
    print(f"정리된 프로필 수: {len(cleaned_data.analyst_profiles)}")
    
    # 품질 보고서 생성
    report = quality_manager.generate_quality_report(test_data, cleaned_data)
    print(f"품질 보고서: {report}")

if __name__ == "__main__":
    test_data_quality_manager()
