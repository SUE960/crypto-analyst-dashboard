"""
분석가 목표가 데이터 모델 정의
암호화폐 분석가들의 목표가, 신뢰도, 예측 정확도 등을 위한 Pydantic 모델들
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum

class AnalysisType(str, Enum):
    """분석 유형"""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    MIXED = "mixed"

class TimeframeType(str, Enum):
    """시간대 유형"""
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"

class AnalystProfile(BaseModel):
    """분석가 프로필 모델"""
    id: Optional[str] = None
    name: str = Field(..., description="분석가 이름")
    source: str = Field(..., description="데이터 소스")
    source_id: Optional[str] = Field(None, description="원본 소스에서의 분석가 ID")
    profile_url: Optional[str] = Field(None, description="프로필 URL")
    bio: Optional[str] = Field(None, description="분석가 소개")
    expertise_areas: List[str] = Field(default_factory=list, description="전문 분야")
    total_predictions: int = Field(default=0, description="총 예측 수")
    accuracy_score: float = Field(default=0.0, ge=0, le=100, description="정확도 점수 (0-100)")
    reliability_score: float = Field(default=0.0, ge=0, le=100, description="신뢰도 점수 (0-100)")
    followers_count: int = Field(default=0, description="팔로워 수")
    is_active: bool = Field(default=True, description="활성 상태")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AnalystTarget(BaseModel):
    """분석가 목표가 모델"""
    id: Optional[str] = None
    analyst_id: Optional[str] = Field(None, description="분석가 ID")
    symbol: str = Field(..., description="코인 심볼")
    current_price: Decimal = Field(..., description="현재 가격")
    target_price: Decimal = Field(..., description="목표 가격")
    price_change_percent: Optional[Decimal] = Field(None, description="목표가 대비 상승률")
    timeframe: TimeframeType = Field(..., description="시간대")
    timeframe_months: Optional[int] = Field(None, description="구체적인 개월 수")
    analysis_type: AnalysisType = Field(..., description="분석 유형")
    confidence_level: int = Field(..., ge=1, le=10, description="신뢰도 레벨 (1-10)")
    reasoning: Optional[str] = Field(None, description="분석 근거")
    key_factors: List[str] = Field(default_factory=list, description="주요 요인들")
    risk_factors: List[str] = Field(default_factory=list, description="리스크 요인들")
    source_url: Optional[str] = Field(None, description="원본 분석 링크")
    published_at: Optional[datetime] = Field(None, description="발행일")
    expires_at: Optional[datetime] = Field(None, description="예측 유효기간")
    is_active: bool = Field(default=True, description="활성 상태")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('price_change_percent', pre=True, always=True)
    def calculate_price_change_percent(cls, v, values):
        """가격 변화율 자동 계산"""
        if v is None and 'current_price' in values and 'target_price' in values:
            current = values['current_price']
            target = values['target_price']
            if current and target and current > 0:
                return ((target - current) / current) * 100
        return v

class PredictionAccuracy(BaseModel):
    """예측 정확도 모델"""
    id: Optional[str] = None
    analyst_id: Optional[str] = Field(None, description="분석가 ID")
    target_id: Optional[str] = Field(None, description="목표가 ID")
    symbol: str = Field(..., description="코인 심볼")
    predicted_price: Decimal = Field(..., description="예측 가격")
    actual_price: Optional[Decimal] = Field(None, description="실제 가격")
    price_accuracy: Optional[Decimal] = Field(None, description="가격 정확도 (%)")
    direction_accuracy: Optional[bool] = Field(None, description="방향성 정확도")
    timeframe: TimeframeType = Field(..., description="시간대")
    prediction_date: datetime = Field(..., description="예측일")
    evaluation_date: Optional[datetime] = Field(None, description="평가일")
    is_evaluated: bool = Field(default=False, description="평가 완료 여부")
    created_at: Optional[datetime] = None

    @validator('price_accuracy', pre=True, always=True)
    def calculate_price_accuracy(cls, v, values):
        """가격 정확도 자동 계산"""
        if v is None and 'predicted_price' in values and 'actual_price' in values:
            predicted = values['predicted_price']
            actual = values['actual_price']
            if predicted and actual and predicted > 0:
                return abs((actual - predicted) / predicted) * 100
        return v

    @validator('direction_accuracy', pre=True, always=True)
    def calculate_direction_accuracy(cls, v, values):
        """방향성 정확도 자동 계산"""
        if v is None and 'predicted_price' in values and 'actual_price' in values:
            predicted = values['predicted_price']
            actual = values['actual_price']
            if predicted and actual:
                # 예측 시점의 가격과 비교해야 하지만, 여기서는 단순화
                return predicted <= actual  # 상승 예측이 맞았는지
        return v

class AnalystReliabilityHistory(BaseModel):
    """분석가 신뢰도 점수 이력 모델"""
    id: Optional[str] = None
    analyst_id: Optional[str] = Field(None, description="분석가 ID")
    reliability_score: float = Field(..., ge=0, le=100, description="신뢰도 점수")
    accuracy_score: float = Field(..., ge=0, le=100, description="정확도 점수")
    total_predictions: int = Field(..., ge=0, description="총 예측 수")
    successful_predictions: int = Field(..., ge=0, description="성공한 예측 수")
    calculation_method: Optional[str] = Field(None, description="계산 방법")
    period_start: datetime = Field(..., description="기간 시작")
    period_end: datetime = Field(..., description="기간 종료")
    created_at: Optional[datetime] = None

class CoinAnalystSummary(BaseModel):
    """코인별 분석가 목표가 집계 모델"""
    id: Optional[str] = None
    symbol: str = Field(..., description="코인 심볼")
    current_price: Decimal = Field(..., description="현재 가격")
    total_analysts: int = Field(default=0, description="총 분석가 수")
    short_term_targets: int = Field(default=0, description="단기 목표가 수")
    medium_term_targets: int = Field(default=0, description="중기 목표가 수")
    long_term_targets: int = Field(default=0, description="장기 목표가 수")
    avg_short_term_target: Optional[Decimal] = Field(None, description="평균 단기 목표가")
    avg_medium_term_target: Optional[Decimal] = Field(None, description="평균 중기 목표가")
    avg_long_term_target: Optional[Decimal] = Field(None, description="평균 장기 목표가")
    median_short_term_target: Optional[Decimal] = Field(None, description="중간값 단기 목표가")
    median_medium_term_target: Optional[Decimal] = Field(None, description="중간값 중기 목표가")
    median_long_term_target: Optional[Decimal] = Field(None, description="중간값 장기 목표가")
    consensus_direction: Optional[str] = Field(None, description="합의 방향")
    confidence_level: Optional[Decimal] = Field(None, description="평균 신뢰도")
    price_dispersion: Optional[Decimal] = Field(None, description="목표가 분산도")
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None

class MarketInsight(BaseModel):
    """시장 인사이트 모델"""
    id: Optional[str] = None
    symbol: str = Field(..., description="코인 심볼")
    type: str = Field(..., description="인사이트 유형")
    content: str = Field(..., description="인사이트 내용")
    source: str = Field(..., description="데이터 소스")
    confidence: int = Field(..., ge=1, le=10, description="신뢰도 (1-10)")
    analysis_type: AnalysisType = Field(..., description="분석 유형")
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class SentimentAnalysis(BaseModel):
    """감성 분석 모델"""
    id: Optional[str] = None
    symbol: str = Field(..., description="코인 심볼")
    sentiment_score: float = Field(..., ge=-1, le=1, description="감성 점수 (-1 ~ 1)")
    confidence: float = Field(..., ge=0, le=1, description="신뢰도 (0 ~ 1)")
    positive_count: int = Field(default=0, description="긍정적 기사 수")
    negative_count: int = Field(default=0, description="부정적 기사 수")
    neutral_count: int = Field(default=0, description="중립적 기사 수")
    total_articles: int = Field(default=0, description="총 기사 수")
    source: str = Field(..., description="데이터 소스")
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class MarketIndex(BaseModel):
    """시장 지수 모델"""
    id: Optional[str] = None
    name: str = Field(..., description="지수 이름")
    value: float = Field(..., description="지수 값")
    change: float = Field(..., description="변화량")
    source: str = Field(..., description="데이터 소스")
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class SectorAnalysis(BaseModel):
    """섹터 분석 모델"""
    id: Optional[str] = None
    metric: str = Field(..., description="지표명")
    value: float = Field(..., description="값")
    percentage: float = Field(..., description="퍼센트")
    source: str = Field(..., description="데이터 소스")
    published_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

# 수집된 데이터를 위한 통합 모델
class CollectedAnalystData(BaseModel):
    """수집된 분석가 데이터 통합 모델"""
    analyst_profiles: List[AnalystProfile] = Field(default_factory=list)
    analyst_targets: List[AnalystTarget] = Field(default_factory=list)
    prediction_accuracy: List[PredictionAccuracy] = Field(default_factory=list)
    analyst_reliability_history: List[AnalystReliabilityHistory] = Field(default_factory=list)
    coin_analyst_summary: List[CoinAnalystSummary] = Field(default_factory=list)
    market_insights: List[MarketInsight] = Field(default_factory=list)
    sentiment_analysis: List[SentimentAnalysis] = Field(default_factory=list)
    market_indices: List[MarketIndex] = Field(default_factory=list)
    sector_analysis: List[SectorAnalysis] = Field(default_factory=list)
    collected_at: datetime = Field(default_factory=datetime.now)
    total_records: int = Field(default=0)

    @validator('total_records', pre=True, always=True)
    def calculate_total_records(cls, v, values):
        """총 레코드 수 자동 계산"""
        total = 0
        for field_name in ['analyst_profiles', 'analyst_targets', 'prediction_accuracy', 
                          'analyst_reliability_history', 'coin_analyst_summary', 
                          'market_insights', 'sentiment_analysis', 'market_indices', 'sector_analysis']:
            if field_name in values:
                total += len(values[field_name])
        return total

# 데이터 검증을 위한 헬퍼 함수들
def validate_price_target(target: AnalystTarget) -> bool:
    """가격 목표가 유효성 검증"""
    if target.current_price <= 0 or target.target_price <= 0:
        return False
    
    # 목표가가 현재가의 0.1배 ~ 10배 범위 내에 있는지 확인
    price_ratio = target.target_price / target.current_price
    if price_ratio < 0.1 or price_ratio > 10:
        return False
    
    return True

def validate_analyst_profile(profile: AnalystProfile) -> bool:
    """분석가 프로필 유효성 검증"""
    if not profile.name or len(profile.name.strip()) < 2:
        return False
    
    if profile.reliability_score < 0 or profile.reliability_score > 100:
        return False
    
    if profile.accuracy_score < 0 or profile.accuracy_score > 100:
        return False
    
    return True

def calculate_consensus_direction(targets: List[AnalystTarget]) -> str:
    """목표가들의 합의 방향 계산"""
    if not targets:
        return "neutral"
    
    bullish_count = 0
    bearish_count = 0
    
    for target in targets:
        if target.price_change_percent:
            if target.price_change_percent > 5:
                bullish_count += 1
            elif target.price_change_percent < -5:
                bearish_count += 1
    
    if bullish_count > bearish_count:
        return "bullish"
    elif bearish_count > bullish_count:
        return "bearish"
    else:
        return "neutral"

def calculate_price_dispersion(targets: List[AnalystTarget]) -> Optional[Decimal]:
    """목표가들의 분산도 계산"""
    if len(targets) < 2:
        return None
    
    prices = [target.target_price for target in targets]
    mean_price = sum(prices) / len(prices)
    
    variance = sum((price - mean_price) ** 2 for price in prices) / len(prices)
    std_dev = variance ** 0.5
    
    return (std_dev / mean_price) * 100 if mean_price > 0 else None
