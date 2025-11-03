"""
CoinGecko 데이터용 Pydantic 모델 정의
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class MarketMetric(BaseModel):
    """시장 메트릭 데이터 모델 (CoinGecko)"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 가격 데이터
    current_price: Optional[Decimal] = None
    price_change_24h: Optional[Decimal] = None
    price_change_percentage_24h: Optional[Decimal] = None
    
    # 시가총액
    market_cap: Optional[Decimal] = None
    market_cap_change_24h: Optional[Decimal] = None
    market_cap_change_percentage_24h: Optional[Decimal] = None
    
    # 거래량
    total_volume: Optional[Decimal] = None
    volume_change_24h: Optional[Decimal] = None
    
    # 순환 공급량
    circulating_supply: Optional[Decimal] = None
    total_supply: Optional[Decimal] = None
    max_supply: Optional[Decimal] = None
    
    # 시장 순위
    market_cap_rank: Optional[int] = None
    
    # 변동성 지표
    price_change_percentage_7d: Optional[Decimal] = None
    price_change_percentage_30d: Optional[Decimal] = None
    price_change_percentage_1y: Optional[Decimal] = None
    
    # 거래소 데이터
    trust_score: Optional[str] = None
    trade_volume_24h: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'coingecko'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
    
    @validator('current_price', 'market_cap', 'total_volume', 'circulating_supply', 
              'total_supply', 'max_supply', 'trade_volume_24h')
    def validate_positive_decimals(cls, v):
        """양수 Decimal 필드 검증"""
        if v is not None and v < 0:
            raise ValueError('값은 0 이상이어야 합니다')
        return v
    
    @validator('market_cap_rank')
    def validate_positive_integers(cls, v):
        """양수 정수 필드 검증"""
        if v is not None and v < 0:
            raise ValueError('값은 0 이상이어야 합니다')
        return v

class PriceHistory(BaseModel):
    """가격 히스토리 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    price: Decimal
    volume: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'coingecko'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('price', 'volume', 'market_cap')
    def validate_positive_values(cls, v):
        """양수 값 검증"""
        if v is not None and v < 0:
            raise ValueError('값은 0 이상이어야 합니다')
        return v

class ExchangeData(BaseModel):
    """거래소 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    exchange_name: str
    trust_score: Optional[str] = None
    trade_volume_24h: Optional[Decimal] = None
    bid_ask_spread_percentage: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'coingecko'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('trust_score')
    def validate_trust_score(cls, v):
        """신뢰도 점수 검증"""
        if v is not None and v not in ['green', 'yellow', 'red']:
            raise ValueError('신뢰도 점수는 green, yellow, red 중 하나여야 합니다')
        return v

# 기존 모델들도 유지 (향후 확장용)
class OnchainMetric(BaseModel):
    """온체인 메트릭 데이터 모델 (CryptoQuant 대체용)"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 거래소 플로우 (CoinGecko에서는 간접적으로 추정)
    exchange_netflow: Optional[Decimal] = None
    exchange_reserve: Optional[Decimal] = None
    
    # 활성 주소 (CoinGecko에서는 제공하지 않음)
    active_addresses: Optional[int] = None
    
    # 트랜잭션 (CoinGecko에서는 제공하지 않음)
    transaction_count: Optional[int] = None
    transaction_volume: Optional[Decimal] = None
    
    # 채굴자 플로우 (CoinGecko에서는 제공하지 않음)
    miner_netflow: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'coingecko_estimated'
    raw_data: Dict[str, Any] = Field(default_factory=dict)

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
    market_dispersion_score: Optional[Decimal] = None  # 시장 데이터 기반
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
    coingecko_id: Optional[str] = None  # CoinGecko ID 추가
    cryptoquant_ticker: Optional[str] = None  # 향후 확장용
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """심볼 검증"""
        if not v or len(v) > 10:
            raise ValueError('심볼은 1-10자 사이여야 합니다')
        return v.upper()
