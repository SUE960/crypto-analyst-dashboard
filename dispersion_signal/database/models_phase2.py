"""
Phase 2 Pydantic 데이터 모델 정의 (CoinMarketCap & CryptoCompare)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class MarketCapData(BaseModel):
    """시가총액 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 시가총액 정보
    market_cap: Optional[Decimal] = None
    market_cap_rank: Optional[int] = None
    fully_diluted_market_cap: Optional[Decimal] = None
    
    # 공급량 정보
    circulating_supply: Optional[Decimal] = None
    total_supply: Optional[Decimal] = None
    max_supply: Optional[Decimal] = None
    
    # 도미넌스
    market_cap_dominance: Optional[Decimal] = None
    
    # ATH/ATL
    ath_price: Optional[Decimal] = None
    ath_date: Optional[datetime] = None
    ath_change_percentage: Optional[Decimal] = None
    atl_price: Optional[Decimal] = None
    atl_date: Optional[datetime] = None
    atl_change_percentage: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'coinmarketcap'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
    
    @validator('market_cap', 'fully_diluted_market_cap')
    def validate_positive_values(cls, v):
        """양수 값 검증"""
        if v is not None and v < 0:
            raise ValueError('시가총액은 0 이상이어야 합니다')
        return v
    
    @validator('market_cap_rank')
    def validate_rank(cls, v):
        """순위 검증"""
        if v is not None and v < 1:
            raise ValueError('순위는 1 이상이어야 합니다')
        return v

class SocialData(BaseModel):
    """소셜 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 트위터 데이터
    twitter_followers: Optional[int] = None
    twitter_following: Optional[int] = None
    twitter_lists: Optional[int] = None
    twitter_favourites: Optional[int] = None
    twitter_statuses: Optional[int] = None
    
    # 레딧 데이터
    reddit_subscribers: Optional[int] = None
    reddit_active_users: Optional[int] = None
    reddit_posts_per_hour: Optional[Decimal] = None
    reddit_comments_per_hour: Optional[Decimal] = None
    
    # 커뮤니티 데이터
    community_score: Optional[Decimal] = None
    public_interest_score: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'cryptocompare'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
    
    @validator('twitter_followers', 'twitter_following', 'twitter_lists', 
               'twitter_favourites', 'twitter_statuses', 'reddit_subscribers', 
               'reddit_active_users')
    def validate_positive_integers(cls, v):
        """양수 정수 검증"""
        if v is not None and v < 0:
            raise ValueError('소셜 메트릭은 0 이상이어야 합니다')
        return v

class NewsSentiment(BaseModel):
    """뉴스 및 감성 데이터 모델"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # 뉴스 정보
    news_count: Optional[int] = None
    news_sources: Optional[List[str]] = None
    
    # 감성 분석
    sentiment_score: Optional[Decimal] = None  # -100 to 100
    sentiment_positive: Optional[int] = None
    sentiment_neutral: Optional[int] = None
    sentiment_negative: Optional[int] = None
    
    # 트렌드
    trending_score: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'cryptocompare'
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
            raise ValueError('감성 점수는 -100에서 100 사이여야 합니다')
        return v
    
    @validator('news_count', 'sentiment_positive', 'sentiment_neutral', 'sentiment_negative')
    def validate_positive_integers(cls, v):
        """양수 정수 검증"""
        if v is not None and v < 0:
            raise ValueError('뉴스 및 감성 메트릭은 0 이상이어야 합니다')
        return v

class GlobalMetrics(BaseModel):
    """글로벌 메트릭 데이터 모델"""
    
    timestamp: datetime
    
    # 전체 시장 데이터
    total_market_cap: Optional[Decimal] = None
    total_volume_24h: Optional[Decimal] = None
    btc_dominance: Optional[Decimal] = None
    eth_dominance: Optional[Decimal] = None
    active_cryptocurrencies: Optional[int] = None
    active_exchanges: Optional[int] = None
    
    # 메타데이터
    data_source: str = 'coinmarketcap'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v
    
    @validator('total_market_cap', 'total_volume_24h')
    def validate_positive_values(cls, v):
        """양수 값 검증"""
        if v is not None and v < 0:
            raise ValueError('시장 데이터는 0 이상이어야 합니다')
        return v
    
    @validator('btc_dominance', 'eth_dominance')
    def validate_dominance(cls, v):
        """도미넌스 검증 (0-100)"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError('도미넌스는 0에서 100 사이여야 합니다')
        return v
    
    @validator('active_cryptocurrencies', 'active_exchanges')
    def validate_positive_integers(cls, v):
        """양수 정수 검증"""
        if v is not None and v < 0:
            raise ValueError('활성 수는 0 이상이어야 합니다')
        return v

# 기존 모델들도 유지 (호환성)
class CryptocurrencyBinance(BaseModel):
    """Binance 코인 마스터 데이터 모델 (기존)"""
    
    id: Optional[UUID] = None
    symbol: str
    name: str
    binance_symbol: str
    market_cap_rank: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """심볼 검증"""
        if not v or len(v) > 10:
            raise ValueError('심볼은 1-10자 사이여야 합니다')
        return v.upper()
    
    @validator('binance_symbol')
    def validate_binance_symbol(cls, v):
        """Binance 심볼 검증"""
        if not v or not v.endswith('USDT'):
            raise ValueError('Binance 심볼은 USDT로 끝나야 합니다')
        return v.upper()

class MarketDataDaily(BaseModel):
    """일일 시장 데이터 모델 (기존)"""
    
    crypto_id: UUID
    date: datetime
    
    # OHLCV 데이터
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    quote_volume: Decimal
    
    # 가격 변화
    price_change_24h: Optional[Decimal] = None
    price_change_percent_24h: Optional[Decimal] = None
    
    # 추가 메트릭
    weighted_avg_price: Optional[Decimal] = None
    prev_close_price: Optional[Decimal] = None
    last_price: Optional[Decimal] = None
    bid_price: Optional[Decimal] = None
    ask_price: Optional[Decimal] = None
    
    # 거래 통계
    trade_count: Optional[int] = None
    first_trade_id: Optional[int] = None
    last_trade_id: Optional[int] = None
    
    # 시간 정보
    open_time: Optional[datetime] = None
    close_time: Optional[datetime] = None
    
    # 메타데이터
    data_source: str = 'binance'
    raw_data: Dict[str, Any] = Field(default_factory=dict)

class PriceHistory(BaseModel):
    """히스토리컬 가격 데이터 모델 (기존)"""
    
    crypto_id: UUID
    timestamp: datetime
    
    # OHLCV 데이터
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    quote_volume: Decimal
    
    # 거래 통계
    trade_count: Optional[int] = None
    taker_buy_volume: Optional[Decimal] = None
    taker_buy_quote_volume: Optional[Decimal] = None
    
    # 메타데이터
    data_source: str = 'binance'
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """타임스탬프 검증"""
        if v.tzinfo is None:
            raise ValueError('타임스탬프는 timezone 정보가 필요합니다')
        return v

class CurrentPrice(BaseModel):
    """현재 가격 데이터 모델 (기존)"""
    
    crypto_id: UUID
    timestamp: datetime
    price: Decimal
    
    # 메타데이터
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
