-- ============================================
-- Dispersion Signal Database Schema
-- ============================================

-- ============================================
-- 1. 코인 마스터 테이블
-- ============================================
CREATE TABLE cryptocurrencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL UNIQUE, -- BTC, ETH, SOL
    name VARCHAR(100) NOT NULL, -- Bitcoin, Ethereum
    cryptoquant_ticker VARCHAR(20), -- CryptoQuant API용 티커
    coingecko_id VARCHAR(50), -- CoinGecko API용 ID
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_crypto_symbol ON cryptocurrencies(symbol);
CREATE INDEX idx_crypto_active ON cryptocurrencies(is_active);

-- ============================================
-- 2. 온체인 메트릭 테이블 (CryptoQuant 데이터)
-- ============================================
CREATE TABLE onchain_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 거래소 플로우 (Exchange Flow)
    exchange_netflow NUMERIC(20, 8), -- 순유출입 (음수=유출, 양수=유입)
    exchange_inflow NUMERIC(20, 8), -- 유입량
    exchange_outflow NUMERIC(20, 8), -- 유출량
    exchange_reserve NUMERIC(20, 8), -- 거래소 잔고
    
    -- 고래 지갑 (Whale Wallets)
    whale_balance_change NUMERIC(20, 8), -- 상위 100개 지갑 보유량 변화
    whale_transaction_count INTEGER, -- 고래 거래 횟수
    
    -- 스테이블코인 (Stablecoin)
    stablecoin_exchange_reserve NUMERIC(20, 8), -- 거래소 스테이블코인 잔고
    stablecoin_inflow NUMERIC(20, 8), -- 스테이블코인 유입 (매수 준비 자금)
    
    -- 온체인 활동 (On-chain Activity)
    active_addresses INTEGER, -- 활성 주소 수
    transaction_count INTEGER, -- 트랜잭션 수
    transaction_volume NUMERIC(20, 8), -- 거래량
    
    -- 채굴자 (Miner) - Bitcoin만 해당
    miner_netflow NUMERIC(20, 8), -- 채굴자 순유출입
    miner_reserve NUMERIC(20, 8), -- 채굴자 보유량
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'cryptoquant',
    raw_data JSONB, -- 원본 API 응답 저장
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- 인덱스
CREATE INDEX idx_onchain_crypto_time ON onchain_metrics(crypto_id, timestamp DESC);
CREATE INDEX idx_onchain_timestamp ON onchain_metrics(timestamp DESC);

-- ============================================
-- 3. 감성 메트릭 테이블 (소셜 미디어)
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
-- 4. 파생상품 메트릭 테이블 (Derivatives)
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
-- 5. 통합 분산도 점수 테이블
-- ============================================
CREATE TABLE dispersion_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 개별 분산도 점수 (0~100, 낮을수록 컨센서스)
    onchain_dispersion_score NUMERIC(5, 2), -- 온체인 컨센서스 분산도
    sentiment_dispersion_score NUMERIC(5, 2), -- 감성 분산도
    derivatives_dispersion_score NUMERIC(5, 2), -- 파생상품 분산도
    
    -- 가중 통합 점수
    weighted_dispersion_score NUMERIC(5, 2), -- 온체인 60% + 감성 30% + 파생 10%
    
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
-- 6. Row Level Security (RLS) 설정
-- ============================================
ALTER TABLE cryptocurrencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE onchain_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE derivatives_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE dispersion_scores ENABLE ROW LEVEL SECURITY;

-- 모든 사용자 읽기 허용
CREATE POLICY "Enable read access for all users" ON cryptocurrencies FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON onchain_metrics FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON sentiment_metrics FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON derivatives_metrics FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON dispersion_scores FOR SELECT USING (true);

-- Service role만 쓰기 허용
CREATE POLICY "Enable insert for service role only" ON onchain_metrics FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Enable insert for service role only" ON sentiment_metrics FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Enable insert for service role only" ON derivatives_metrics FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');
CREATE POLICY "Enable insert for service role only" ON dispersion_scores FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 7. 기본 데이터 삽입
-- ============================================
INSERT INTO cryptocurrencies (symbol, name, cryptoquant_ticker, coingecko_id) VALUES
('BTC', 'Bitcoin', 'btc', 'bitcoin'),
('ETH', 'Ethereum', 'eth', 'ethereum'),
('SOL', 'Solana', 'sol', 'solana'),
('XRP', 'Ripple', 'xrp', 'ripple'),
('BNB', 'BNB', 'bnb', 'binancecoin');
