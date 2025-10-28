"""
Phase 3 Pydantic 데이터 모델 정의 (분산도 신호)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal

class DispersionSignal(BaseModel):
    """분산도 신호 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 가격 분산도
    price_dispersion: Optional[Decimal] = None  # %
    price_sources: Optional[int] = None  # 데이터 소스 수
    price_max: Optional[Decimal] = None
    price_min: Optional[Decimal] = None
    price_avg: Optional[Decimal] = None
    
    # 거래량 분산도
    volume_concentration: Optional[Decimal] = None  # HHI
    volume_total: Optional[Decimal] = None
    
    # 도미넌스 변화
    btc_dominance: Optional[Decimal] = None
    btc_dominance_change_7d: Optional[Decimal] = None
    eth_dominance: Optional[Decimal] = None
    eth_dominance_change_7d: Optional[Decimal] = None
    
    # 신호 레벨
    signal_level: Optional[int] = None  # 1-5
    signal_type: Optional[str] = None  # 'convergence', 'divergence', 'neutral'
    
    # 메타데이터
    data_sources: Optional[List[str]] = None
    calculation_method: Optional[str] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
    
    @validator('price_dispersion')
    def validate_price_dispersion(cls, v):
        """가격 분산도 검증 (0-100%)"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('가격 분산도는 0-100% 범위여야 합니다')
        return v
    
    @validator('volume_concentration')
    def validate_volume_concentration(cls, v):
        """거래량 집중도 검증 (0-10000)"""
        if v is not None and (v < 0 or v > 10000):
            raise ValueError('거래량 집중도는 0-10000 범위여야 합니다')
        return v
    
    @validator('signal_level')
    def validate_signal_level(cls, v):
        """신호 레벨 검증 (1-5)"""
        if v is not None and (v < 1 or v > 5):
            raise ValueError('신호 레벨은 1-5 범위여야 합니다')
        return v
    
    @validator('signal_type')
    def validate_signal_type(cls, v):
        """신호 타입 검증"""
        if v is not None and v not in ['convergence', 'divergence', 'neutral']:
            raise ValueError('신호 타입은 convergence, divergence, neutral 중 하나여야 합니다')
        return v
    
    @validator('btc_dominance', 'eth_dominance')
    def validate_dominance(cls, v):
        """도미넌스 검증 (0-100)"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('도미넌스는 0-100% 범위여야 합니다')
        return v

class DispersionSummaryDaily(BaseModel):
    """일일 분산도 요약 데이터 모델"""
    
    date: date
    
    # 전체 시장 분산도
    market_dispersion_avg: Optional[Decimal] = None
    market_dispersion_max: Optional[Decimal] = None
    market_dispersion_min: Optional[Decimal] = None
    
    # 상위 코인별 분산도
    top_dispersion_coins: Optional[List[str]] = None
    low_dispersion_coins: Optional[List[str]] = None
    
    # 도미넌스 요약
    btc_dominance_avg: Optional[Decimal] = None
    eth_dominance_avg: Optional[Decimal] = None
    
    # 신호 통계
    high_signal_count: Optional[int] = None
    low_signal_count: Optional[int] = None
    
    # 메타데이터
    coins_analyzed: Optional[int] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('market_dispersion_avg', 'market_dispersion_max', 'market_dispersion_min')
    def validate_market_dispersion(cls, v):
        """시장 분산도 검증 (0-100%)"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('시장 분산도는 0-100% 범위여야 합니다')
        return v
    
    @validator('btc_dominance_avg', 'eth_dominance_avg')
    def validate_dominance_avg(cls, v):
        """평균 도미넌스 검증 (0-100)"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('평균 도미넌스는 0-100% 범위여야 합니다')
        return v
    
    @validator('high_signal_count', 'low_signal_count', 'coins_analyzed')
    def validate_counts(cls, v):
        """카운트 검증 (0 이상)"""
        if v is not None and v < 0:
            raise ValueError('카운트는 0 이상이어야 합니다')
        return v

# 기존 모델들도 유지 (호환성)
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

class SocialDataPhase2(BaseModel):
    """Phase 2 소셜 데이터 모델 (기존)"""
    
    crypto_id: UUID
    timestamp: datetime
    twitter_followers: Optional[int] = None
    twitter_following: Optional[int] = None
    twitter_lists: Optional[int] = None
    twitter_favourites: Optional[int] = None
    twitter_statuses: Optional[int] = None
    reddit_subscribers: Optional[int] = None
    reddit_active_users: Optional[int] = None
    reddit_posts_per_hour: Optional[Decimal] = None
    reddit_comments_per_hour: Optional[Decimal] = None
    community_score: Optional[Decimal] = None
    public_interest_score: Optional[Decimal] = None
    data_source: str = 'cryptocompare'
    raw_data: Dict[str, Any] = Field(default_factory=dict)

class NewsSentimentPhase2(BaseModel):
    """Phase 2 뉴스 감성 데이터 모델 (기존)"""
    
    crypto_id: UUID
    timestamp: datetime
    news_count: Optional[int] = None
    news_sources: Optional[List[str]] = None
    sentiment_score: Optional[Decimal] = None  # -100 to 100
    sentiment_positive: Optional[int] = None
    sentiment_neutral: Optional[int] = None
    sentiment_negative: Optional[int] = None
    trending_score: Optional[Decimal] = None
    data_source: str = 'cryptocompare'
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
class CryptocurrencyBinance(BaseModel):
    """Binance 코인 마스터 데이터 모델 (Phase 1)"""
    
    id: Optional[UUID] = None
    symbol: str
    name: str
    binance_symbol: str
    market_cap_rank: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MarketDataDaily(BaseModel):
    """일일 시장 데이터 모델 (Phase 1)"""
    
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

class PriceHistory(BaseModel):
    """히스토리컬 가격 데이터 모델 (Phase 1)"""
    
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

class CurrentPrice(BaseModel):
    """현재 가격 데이터 모델 (Phase 1)"""
    
    crypto_id: UUID
    timestamp: datetime
    price: Decimal
    data_source: str = 'binance'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
    
    @validator('price')
    def validate_price(cls, v):
        """가격 검증"""
        if v is not None and v < 0:
            raise ValueError('가격은 0 이상이어야 합니다')
        return v
