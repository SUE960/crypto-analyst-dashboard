-- ============================================
-- Dispersion Signal Database Schema (CoinGecko 버전)
-- 무료 API 사용을 위한 수정된 스키마
-- ============================================

-- ============================================
-- 1. 코인 마스터 테이블 (CoinGecko ID 추가)
-- ============================================
CREATE TABLE cryptocurrencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL UNIQUE, -- BTC, ETH, SOL
    name VARCHAR(100) NOT NULL, -- Bitcoin, Ethereum
    coingecko_id VARCHAR(50), -- CoinGecko API용 ID (bitcoin, ethereum)
    cryptoquant_ticker VARCHAR(20), -- 향후 확장용
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_crypto_symbol ON cryptocurrencies(symbol);
CREATE INDEX idx_crypto_coingecko_id ON cryptocurrencies(coingecko_id);
CREATE INDEX idx_crypto_active ON cryptocurrencies(is_active);

-- ============================================
-- 2. 시장 메트릭 테이블 (CoinGecko 데이터)
-- ============================================
CREATE TABLE market_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 가격 데이터
    current_price NUMERIC(20, 8), -- 현재 가격 (USD)
    price_change_24h NUMERIC(20, 8), -- 24시간 가격 변화
    price_change_percentage_24h NUMERIC(10, 4), -- 24시간 가격 변화율 (%)
    
    -- 시가총액
    market_cap NUMERIC(20, 2), -- 시가총액 (USD)
    market_cap_change_24h NUMERIC(20, 2), -- 24시간 시가총액 변화
    market_cap_change_percentage_24h NUMERIC(10, 4), -- 24시간 시가총액 변화율 (%)
    
    -- 거래량
    total_volume NUMERIC(20, 2), -- 총 거래량 (USD)
    volume_change_24h NUMERIC(20, 2), -- 24시간 거래량 변화
    
    -- 순환 공급량
    circulating_supply NUMERIC(20, 2), -- 순환 공급량
    total_supply NUMERIC(20, 2), -- 총 공급량
    max_supply NUMERIC(20, 2), -- 최대 공급량
    
    -- 시장 순위
    market_cap_rank INTEGER, -- 시가총액 순위
    
    -- 변동성 지표
    price_change_percentage_7d NUMERIC(10, 4), -- 7일 가격 변화율 (%)
    price_change_percentage_30d NUMERIC(10, 4), -- 30일 가격 변화율 (%)
    price_change_percentage_1y NUMERIC(10, 4), -- 1년 가격 변화율 (%)
    
    -- 거래소 데이터
    trust_score VARCHAR(10), -- 신뢰도 점수 (green, yellow, red)
    trade_volume_24h NUMERIC(20, 2), -- 거래소별 24시간 거래량
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'coingecko',
    raw_data JSONB, -- 원본 API 응답 저장
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- 인덱스
CREATE INDEX idx_market_crypto_time ON market_metrics(crypto_id, timestamp DESC);
CREATE INDEX idx_market_timestamp ON market_metrics(timestamp DESC);
CREATE INDEX idx_market_cap_rank ON market_metrics(market_cap_rank);

-- ============================================
-- 3. 가격 히스토리 테이블
-- ============================================
CREATE TABLE price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 가격 데이터
    price NUMERIC(20, 8) NOT NULL, -- 가격 (USD)
    volume NUMERIC(20, 2), -- 거래량 (USD)
    market_cap NUMERIC(20, 2), -- 시가총액 (USD)
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'coingecko',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- 인덱스
CREATE INDEX idx_price_crypto_time ON price_history(crypto_id, timestamp DESC);
CREATE INDEX idx_price_timestamp ON price_history(timestamp DESC);

-- ============================================
-- 4. 거래소 데이터 테이블
-- ============================================
CREATE TABLE exchange_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 거래소 정보
    exchange_name VARCHAR(100) NOT NULL, -- 거래소 이름
    trust_score VARCHAR(10), -- 신뢰도 점수
    trade_volume_24h NUMERIC(20, 2), -- 24시간 거래량
    bid_ask_spread_percentage NUMERIC(10, 4), -- 매수-매도 스프레드 (%)
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'coingecko',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, exchange_name, data_source)
);

-- 인덱스
CREATE INDEX idx_exchange_crypto_time ON exchange_data(crypto_id, timestamp DESC);
CREATE INDEX idx_exchange_name ON exchange_data(exchange_name);

-- ============================================
-- 5. 감성 메트릭 테이블 (소셜 미디어) - 기존 유지
-- ============================================
CREATE TABLE sentiment_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 트위터 감성
    twitter_positive_count INTEGER DEFAULT 0,
    twitter_negative_count INTEGER DEFAULT 0,
    twitter_neutral_count INTEGER DEFAULT 0,
    twitter_sentiment_score NUMERIC(5, 4), -- -1.0 ~ 1.0
    twitter_volume INTEGER, -- 트윗 총량
    
    -- 레딧 감성
    reddit_positive_count INTEGER DEFAULT 0,
    reddit_negative_count INTEGER DEFAULT 0,
    reddit_neutral_count INTEGER DEFAULT 0,
    reddit_sentiment_score NUMERIC(5, 4),
    reddit_volume INTEGER,
    
    -- 인플루언서 감성 (팔로워 10만+ 계정)
    influencer_bullish_count INTEGER DEFAULT 0,
    influencer_bearish_count INTEGER DEFAULT 0,
    influencer_neutral_count INTEGER DEFAULT 0,
    
    -- 통합 감성 점수
    aggregate_sentiment_score NUMERIC(5, 4), -- 전체 평균
    sentiment_dispersion NUMERIC(5, 4), -- 감성 분산도 (표준편차)
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'twitter_api',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- 인덱스
CREATE INDEX idx_sentiment_crypto_time ON sentiment_metrics(crypto_id, timestamp DESC);
CREATE INDEX idx_sentiment_timestamp ON sentiment_metrics(timestamp DESC);

-- ============================================
-- 6. 파생상품 메트릭 테이블 (Derivatives) - 기존 유지
-- ============================================
CREATE TABLE derivatives_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 펀딩비 (Funding Rate)
    binance_funding_rate NUMERIC(10, 8),
    bybit_funding_rate NUMERIC(10, 8),
    okx_funding_rate NUMERIC(10, 8),
    avg_funding_rate NUMERIC(10, 8), -- 평균 펀딩비
    funding_rate_dispersion NUMERIC(10, 8), -- 펀딩비 분산도 (표준편차)
    
    -- 미결제약정 (Open Interest)
    total_open_interest NUMERIC(20, 8),
    oi_change_24h NUMERIC(10, 4), -- 24시간 OI 변화율 (%)
    
    -- 청산 (Liquidations)
    long_liquidation_24h NUMERIC(20, 8),
    short_liquidation_24h NUMERIC(20, 8),
    liquidation_ratio NUMERIC(10, 4), -- Long/Short 청산 비율
    
    -- 현물-선물 프리미엄
    spot_futures_premium NUMERIC(10, 4), -- 프리미엄 (%)
    
    -- 거래량
    spot_volume_24h NUMERIC(20, 8),
    futures_volume_24h NUMERIC(20, 8),
    volume_ratio NUMERIC(10, 4), -- Futures/Spot 비율
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'binance_api',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- 인덱스
CREATE INDEX idx_derivatives_crypto_time ON derivatives_metrics(crypto_id, timestamp DESC);
CREATE INDEX idx_derivatives_timestamp ON derivatives_metrics(timestamp DESC);

-- ============================================
-- 7. 통합 분산도 점수 테이블 (수정됨)
-- ============================================
CREATE TABLE dispersion_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 개별 분산도 점수 (0~100, 낮을수록 컨센서스)
    market_dispersion_score NUMERIC(5, 2), -- 시장 데이터 기반 분산도
    sentiment_dispersion_score NUMERIC(5, 2), -- 감성 분산도
    derivatives_dispersion_score NUMERIC(5, 2), -- 파생상품 분산도
    
    -- 가중 통합 점수
    weighted_dispersion_score NUMERIC(5, 2), -- 시장 60% + 감성 30% + 파생 10%
    
    -- 등급 (A~F)
    grade VARCHAR(1) CHECK (grade IN ('A', 'B', 'C', 'D', 'F')),
    
    -- 투자 신호
    signal_type VARCHAR(20), -- 'STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'VOLATILITY_WARNING'
    signal_confidence NUMERIC(5, 2), -- 신호 신뢰도 (0~100)
    
    -- 예측 (참고용)
    predicted_direction VARCHAR(10), -- 'UP', 'DOWN', 'SIDEWAYS'
    predicted_volatility VARCHAR(10), -- 'LOW', 'MEDIUM', 'HIGH'
    
    -- 메타데이터
    calculation_method VARCHAR(50) DEFAULT 'weighted_average_v1',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp)
);

-- 인덱스
CREATE INDEX idx_dispersion_crypto_time ON dispersion_scores(crypto_id, timestamp DESC);
CREATE INDEX idx_dispersion_grade ON dispersion_scores(grade);
CREATE INDEX idx_dispersion_signal ON dispersion_scores(signal_type);

-- ============================================
-- 8. Row Level Security (RLS) 설정
-- ============================================
ALTER TABLE cryptocurrencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE exchange_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE derivatives_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE dispersion_scores ENABLE ROW LEVEL SECURITY;

-- 모든 사용자 읽기 허용
CREATE POLICY "Enable read access for all users" ON cryptocurrencies FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON market_metrics FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON price_history FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON exchange_data FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON sentiment_metrics FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON derivatives_metrics FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON dispersion_scores FOR SELECT USING (true);

-- Service role만 쓰기 허용
CREATE POLICY "Enable insert for service role only" ON market_metrics FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Enable insert for service role only" ON price_history FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Enable insert for service role only" ON exchange_data FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Enable insert for service role only" ON sentiment_metrics FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Enable insert for service role only" ON derivatives_metrics FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Enable insert for service role only" ON dispersion_scores FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 9. 기본 데이터 삽입 (CoinGecko ID 포함)
-- ============================================
INSERT INTO cryptocurrencies (symbol, name, coingecko_id) VALUES
('BTC', 'Bitcoin', 'bitcoin'),
('ETH', 'Ethereum', 'ethereum'),
('SOL', 'Solana', 'solana'),
('XRP', 'Ripple', 'ripple'),
('BNB', 'BNB', 'binancecoin'),
('ADA', 'Cardano', 'cardano'),
('DOGE', 'Dogecoin', 'dogecoin'),
('MATIC', 'Polygon', 'matic-network'),
('DOT', 'Polkadot', 'polkadot'),
('AVAX', 'Avalanche', 'avalanche-2');
