"""
Phase 4 Pydantic 데이터 모델 정의 (다중 소스 데이터 및 감성 분석)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class MultiSourcePrice(BaseModel):
    """다중 소스 가격 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 소스별 가격
    binance_price: Optional[Decimal] = None
    coinmarketcap_price: Optional[Decimal] = None
    coincap_price: Optional[Decimal] = None
    coinpaprika_price: Optional[Decimal] = None
    coingecko_price: Optional[Decimal] = None
    
    # 통계
    price_sources_count: int
    price_avg: Decimal
    price_std_dev: Optional[Decimal] = None
    price_dispersion: Decimal  # %
    
    # 메타데이터
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
    
    @validator('price_dispersion')
    def validate_price_dispersion(cls, v):
        """가격 분산도 검증 (0-1000%) - 이상치 허용"""
        if v is not None and v < 0:
            raise ValueError('가격 분산도는 0 이상이어야 합니다')
        return v
    
    @validator('price_sources_count')
    def validate_price_sources_count(cls, v):
        """가격 소스 수 검증 (1-5)"""
        if v < 1 or v > 5:
            raise ValueError('가격 소스 수는 1-5 범위여야 합니다')
        return v

class RedditSentiment(BaseModel):
    """Reddit 커뮤니티 감성 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 언급 통계
    total_mentions: int
    positive_mentions: int
    negative_mentions: int
    neutral_mentions: int
    
    # 서브레딧별 분석
    subreddit_breakdown: Dict[str, Any] = Field(default_factory=dict)
    
    # 감성 점수
    sentiment_score: Decimal  # -100 to 100
    community_interest: Decimal  # 0-100
    
    # 메타데이터
    data_source: str = 'reddit'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
    
    @validator('sentiment_score')
    def validate_sentiment_score(cls, v):
        """감성 점수 검증 (-100 to 100)"""
        if v is not None and (v < -100 or v > 100):
            raise ValueError('감성 점수는 -100 to 100 범위여야 합니다')
        return v
    
    @validator('community_interest')
    def validate_community_interest(cls, v):
        """커뮤니티 관심도 검증 (0-100)"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('커뮤니티 관심도는 0-100 범위여야 합니다')
        return v
    
    @validator('total_mentions', 'positive_mentions', 'negative_mentions', 'neutral_mentions')
    def validate_mentions(cls, v):
        """언급 수 검증 (0 이상)"""
        if v is not None and v < 0:
            raise ValueError('언급 수는 0 이상이어야 합니다')
        return v

class EnhancedDispersionSignal(BaseModel):
    """향상된 분산도 신호 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 다중 소스 분산도
    price_dispersion: Decimal
    price_sources: int
    
    # 커뮤니티 감성
    reddit_sentiment_score: Optional[Decimal] = None
    reddit_mention_count: Optional[int] = None
    
    # 통합 신호
    signal_level: int  # 1-5
    signal_type: str
    confidence_score: Decimal  # 0-100
    
    # 메타데이터
    data_sources: List[str] = Field(default_factory=list)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
    
    @validator('price_dispersion')
    def validate_price_dispersion(cls, v):
        """가격 분산도 검증 (0-1000%) - 이상치 허용"""
        if v is not None and v < 0:
            raise ValueError('가격 분산도는 0 이상이어야 합니다')
        return v
    
    @validator('price_sources')
    def validate_price_sources(cls, v):
        """가격 소스 수 검증 (1-5)"""
        if v < 1 or v > 5:
            raise ValueError('가격 소스 수는 1-5 범위여야 합니다')
        return v
    
    @validator('signal_level')
    def validate_signal_level(cls, v):
        """신호 레벨 검증 (1-5)"""
        if v < 1 or v > 5:
            raise ValueError('신호 레벨은 1-5 범위여야 합니다')
        return v
    
    @validator('signal_type')
    def validate_signal_type(cls, v):
        """신호 타입 검증"""
        if v not in ['convergence', 'divergence', 'neutral', 'high_volatility', 'low_volatility']:
            raise ValueError('신호 타입은 convergence, divergence, neutral, high_volatility, low_volatility 중 하나여야 합니다')
        return v
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        """신뢰도 점수 검증 (0-100)"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('신뢰도 점수는 0-100 범위여야 합니다')
        return v
    
    @validator('reddit_sentiment_score')
    def validate_reddit_sentiment_score(cls, v):
        """Reddit 감성 점수 검증 (-100 to 100)"""
        if v is not None and (v < -100 or v > 100):
            raise ValueError('Reddit 감성 점수는 -100 to 100 범위여야 합니다')
        return v

# 기존 모델들도 유지 (호환성)
class DispersionSignalPhase3(BaseModel):
    """Phase 3 분산도 신호 데이터 모델 (기존)"""
    
    crypto_id: UUID
    timestamp: datetime
    price_dispersion: Optional[Decimal] = None
    price_sources: Optional[int] = None
    price_max: Optional[Decimal] = None
    price_min: Optional[Decimal] = None
    price_avg: Optional[Decimal] = None
    volume_concentration: Optional[Decimal] = None
    volume_total: Optional[Decimal] = None
    btc_dominance: Optional[Decimal] = None
    btc_dominance_change_7d: Optional[Decimal] = None
    eth_dominance: Optional[Decimal] = None
    eth_dominance_change_7d: Optional[Decimal] = None
    signal_level: Optional[int] = None
    signal_type: Optional[str] = None
    data_sources: Optional[List[str]] = None
    calculation_method: Optional[str] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)

class DispersionSummaryDailyPhase3(BaseModel):
    """Phase 3 일일 분산도 요약 데이터 모델 (기존)"""
    
    date: datetime
    market_dispersion_avg: Optional[Decimal] = None
    market_dispersion_max: Optional[Decimal] = None
    market_dispersion_min: Optional[Decimal] = None
    top_dispersion_coins: Optional[List[str]] = None
    low_dispersion_coins: Optional[List[str]] = None
    btc_dominance_avg: Optional[Decimal] = None
    eth_dominance_avg: Optional[Decimal] = None
    high_signal_count: Optional[int] = None
    low_signal_count: Optional[int] = None
    coins_analyzed: Optional[int] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)

# Phase 2 모델들도 유지 (호환성)
class MarketCapDataPhase2(BaseModel):
    """Phase 2 시가총액 데이터 모델 (기존)"""
    
    crypto_id: UUID
    timestamp: datetime
    market_cap: Optional[Decimal] = None
    market_cap_rank: Optional[int] = None
    fully_diluted_market_cap: Optional[Decimal] = None
    circulating_supply: Optional[Decimal] = None
    total_supply: Optional[Decimal] = None
    max_supply: Optional[Decimal] = None
    market_cap_dominance: Optional[Decimal] = None
    ath_price: Optional[Decimal] = None
    ath_date: Optional[datetime] = None
    ath_change_percentage: Optional[Decimal] = None
    atl_price: Optional[Decimal] = None
    atl_date: Optional[datetime] = None
    atl_change_percentage: Optional[Decimal] = None
    data_source: str = 'coinmarketcap'
    raw_data: Dict[str, Any] = Field(default_factory=dict)

class GlobalMetricsPhase2(BaseModel):
    """Phase 2 글로벌 메트릭 데이터 모델 (기존)"""
    
    timestamp: datetime
    total_market_cap: Optional[Decimal] = None
    total_volume_24h: Optional[Decimal] = None
    btc_dominance: Optional[Decimal] = None
    eth_dominance: Optional[Decimal] = None
    active_cryptocurrencies: Optional[int] = None
    active_exchanges: Optional[int] = None
    data_source: str = 'coinmarketcap'
    raw_data: Dict[str, Any] = Field(default_factory=dict)

# Phase 1 모델들도 유지 (호환성)
class MarketDataDailyPhase1(BaseModel):
    """Phase 1 일일 시장 데이터 모델 (기존)"""
    
    crypto_id: UUID
    date: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    quote_volume: Decimal
    price_change_24h: Optional[Decimal] = None
    price_change_percent_24h: Optional[Decimal] = None
    weighted_avg_price: Optional[Decimal] = None
    prev_close_price: Optional[Decimal] = None
    last_price: Optional[Decimal] = None
    bid_price: Optional[Decimal] = None
    ask_price: Optional[Decimal] = None
    trade_count: Optional[int] = None
    first_trade_id: Optional[int] = None
    last_trade_id: Optional[int] = None
    open_time: Optional[datetime] = None
    close_time: Optional[datetime] = None
    data_source: str = 'binance'
    raw_data: Dict[str, Any] = Field(default_factory=dict)

class PriceHistoryPhase1(BaseModel):
    """Phase 1 히스토리컬 가격 데이터 모델 (기존)"""
    
    crypto_id: UUID
    timestamp: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    quote_volume: Decimal
    trade_count: Optional[int] = None
    taker_buy_volume: Optional[Decimal] = None
    taker_buy_quote_volume: Optional[Decimal] = None
    data_source: str = 'binance'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
