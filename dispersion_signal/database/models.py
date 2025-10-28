"""
Pydantic 데이터 모델 정의
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class OnchainMetric(BaseModel):
    """온체인 메트릭 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 거래소 플로우
    exchange_netflow: Optional[Decimal] = None
    exchange_inflow: Optional[Decimal] = None
    exchange_outflow: Optional[Decimal] = None
    exchange_reserve: Optional[Decimal] = None
    
    # 고래 지갑
    whale_balance_change: Optional[Decimal] = None
    whale_transaction_count: Optional[int] = None
    
    # 스테이블코인
    stablecoin_exchange_reserve: Optional[Decimal] = None
    stablecoin_inflow: Optional[Decimal] = None
    
    # 온체인 활동
    active_addresses: Optional[int] = None
    transaction_count: Optional[int] = None
    transaction_volume: Optional[Decimal] = None
    
    # 채굴자 (Bitcoin만)
    miner_netflow: Optional[Decimal] = None
    miner_reserve: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'cryptoquant'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
    
    @validator('exchange_netflow', 'exchange_inflow', 'exchange_outflow', 'exchange_reserve',
              'whale_balance_change', 'stablecoin_exchange_reserve', 'stablecoin_inflow',
              'transaction_volume', 'miner_netflow', 'miner_reserve')
    def validate_decimal_fields(cls, v):
        """Decimal 필드 검증"""
        if v is not None and v < 0:
            # 음수 값도 허용 (예: 넷플로우)
            pass
        return v
    
    @validator('active_addresses', 'transaction_count', 'whale_transaction_count')
    def validate_positive_integers(cls, v):
        """양수 정수 필드 검증"""
        if v is not None and v < 0:
            raise ValueError('값은 0 이상이어야 합니다')
        return v

class SentimentMetric(BaseModel):
    """감성 메트릭 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 트위터 감성
    twitter_positive_count: int = 0
    twitter_negative_count: int = 0
    twitter_neutral_count: int = 0
    twitter_sentiment_score: Optional[Decimal] = None
    twitter_volume: Optional[int] = None
    
    # 레딧 감성
    reddit_positive_count: int = 0
    reddit_negative_count: int = 0
    reddit_neutral_count: int = 0
    reddit_sentiment_score: Optional[Decimal] = None
    reddit_volume: Optional[int] = None
    
    # 인플루언서 감성
    influencer_bullish_count: int = 0
    influencer_bearish_count: int = 0
    influencer_neutral_count: int = 0
    
    # 통합 감성 점수
    aggregate_sentiment_score: Optional[Decimal] = None
    sentiment_dispersion: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'twitter_api'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('twitter_sentiment_score', 'reddit_sentiment_score', 'aggregate_sentiment_score')
    def validate_sentiment_score(cls, v):
        """감성 점수 검증 (-1.0 ~ 1.0)"""
        if v is not None:
            if v < -1.0 or v > 1.0:
                raise ValueError('감성 점수는 -1.0과 1.0 사이여야 합니다')
        return v

class DerivativesMetric(BaseModel):
    """파생상품 메트릭 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 펀딩비
    binance_funding_rate: Optional[Decimal] = None
    bybit_funding_rate: Optional[Decimal] = None
    okx_funding_rate: Optional[Decimal] = None
    avg_funding_rate: Optional[Decimal] = None
    funding_rate_dispersion: Optional[Decimal] = None
    
    # 미결제약정
    total_open_interest: Optional[Decimal] = None
    oi_change_24h: Optional[Decimal] = None
    
    # 청산
    long_liquidation_24h: Optional[Decimal] = None
    short_liquidation_24h: Optional[Decimal] = None
    liquidation_ratio: Optional[Decimal] = None
    
    # 현물-선물 프리미엄
    spot_futures_premium: Optional[Decimal] = None
    
    # 거래량
    spot_volume_24h: Optional[Decimal] = None
    futures_volume_24h: Optional[Decimal] = None
    volume_ratio: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'binance_api'
    raw_data: Dict[str, Any] = Field(default_factory=dict)

class DispersionScore(BaseModel):
    """통합 분산도 점수 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 개별 분산도 점수 (0~100)
    onchain_dispersion_score: Optional[Decimal] = None
    sentiment_dispersion_score: Optional[Decimal] = None
    derivatives_dispersion_score: Optional[Decimal] = None
    
    # 가중 통합 점수
    weighted_dispersion_score: Optional[Decimal] = None
    
    # 등급
    grade: Optional[str] = None
    
    # 투자 신호
    signal_type: Optional[str] = None
    signal_confidence: Optional[Decimal] = None
    
    # 예측
    predicted_direction: Optional[str] = None
    predicted_volatility: Optional[str] = None
    
    # 메타데이터
    calculation_method: str = 'weighted_average_v1'
    
    @validator('grade')
    def validate_grade(cls, v):
        """등급 검증"""
        if v is not None and v not in ['A', 'B', 'C', 'D', 'F']:
            raise ValueError('등급은 A, B, C, D, F 중 하나여야 합니다')
        return v
    
    @validator('signal_type')
    def validate_signal_type(cls, v):
        """신호 타입 검증"""
        if v is not None and v not in ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'VOLATILITY_WARNING']:
            raise ValueError('신호 타입이 올바르지 않습니다')
        return v
    
    @validator('predicted_direction')
    def validate_predicted_direction(cls, v):
        """예측 방향 검증"""
        if v is not None and v not in ['UP', 'DOWN', 'SIDEWAYS']:
            raise ValueError('예측 방향은 UP, DOWN, SIDEWAYS 중 하나여야 합니다')
        return v
    
    @validator('predicted_volatility')
    def validate_predicted_volatility(cls, v):
        """예측 변동성 검증"""
        if v is not None and v not in ['LOW', 'MEDIUM', 'HIGH']:
            raise ValueError('예측 변동성은 LOW, MEDIUM, HIGH 중 하나여야 합니다')
        return v

class Cryptocurrency(BaseModel):
    """암호화폐 마스터 데이터 모델"""
    
    id: Optional[UUID] = None
    symbol: str
    name: str
    cryptoquant_ticker: Optional[str] = None
    coingecko_id: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """심볼 검증"""
        if not v or len(v) > 10:
            raise ValueError('심볼은 1-10자 사이여야 합니다')
        return v.upper()
