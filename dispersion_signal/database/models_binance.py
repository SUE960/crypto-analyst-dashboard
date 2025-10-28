"""
Binance API용 Pydantic 데이터 모델 정의
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal

class CryptocurrencyBinance(BaseModel):
    """Binance 코인 마스터 데이터 모델"""
    
    id: Optional[UUID] = None
    symbol: str
    name: str
    binance_symbol: str  # BTCUSDT 형식
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
    """일일 시장 데이터 모델"""
    
    crypto_id: UUID
    date: date
    
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
    
    @validator('open_price', 'high_price', 'low_price', 'close_price', 'volume', 'quote_volume')
    def validate_positive_prices(cls, v):
        """양수 가격/거래량 검증"""
        if v is not None and v < 0:
            raise ValueError('가격과 거래량은 0 이상이어야 합니다')
        return v
    
    @validator('high_price')
    def validate_high_price(cls, v, values):
        """고가가 시가, 저가, 종가보다 높은지 검증"""
        if 'open_price' in values and 'low_price' in values and 'close_price' in values:
            open_price = values['open_price']
            low_price = values['low_price']
            close_price = values['close_price']
            
            if v < max(open_price, low_price, close_price):
                raise ValueError('고가는 시가, 저가, 종가 중 최대값보다 높아야 합니다')
        return v
    
    @validator('low_price')
    def validate_low_price(cls, v, values):
        """저가가 시가, 고가, 종가보다 낮은지 검증"""
        if 'open_price' in values and 'high_price' in values and 'close_price' in values:
            open_price = values['open_price']
            high_price = values['high_price']
            close_price = values['close_price']
            
            if v > min(open_price, high_price, close_price):
                raise ValueError('저가는 시가, 고가, 종가 중 최소값보다 낮아야 합니다')
        return v

class PriceHistory(BaseModel):
    """히스토리컬 가격 데이터 모델"""
    
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
    
    @validator('open_price', 'high_price', 'low_price', 'close_price', 'volume', 'quote_volume')
    def validate_positive_values(cls, v):
        """양수 값 검증"""
        if v is not None and v < 0:
            raise ValueError('값은 0 이상이어야 합니다')
        return v

class CurrentPrice(BaseModel):
    """현재 가격 데이터 모델"""
    
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

class TopCoin(BaseModel):
    """상위 코인 정보 모델"""
    
    symbol: str
    name: str
    binance_symbol: str
    market_cap_rank: int
    quote_volume: Decimal
    last_price: Decimal
    price_change_percent: Decimal
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """심볼 검증"""
        if not v or len(v) > 10:
            raise ValueError('심볼은 1-10자 사이여야 합니다')
        return v.upper()
    
    @validator('market_cap_rank')
    def validate_rank(cls, v):
        """순위 검증"""
        if v is not None and v < 1:
            raise ValueError('순위는 1 이상이어야 합니다')
        return v

# 기존 모델들도 유지 (향후 확장용)
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
    market_dispersion_score: Optional[Decimal] = None
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
