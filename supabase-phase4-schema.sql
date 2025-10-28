-- ============================================
-- Dispersion Signal Database Schema (Phase 4)
-- 다중 소스 데이터 연동 및 감성 분석
-- ============================================

-- ============================================
-- 1. 다중 소스 가격 데이터 테이블
-- ============================================
CREATE TABLE IF NOT EXISTS multi_source_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 소스별 가격
    binance_price NUMERIC(20, 8),
    coinmarketcap_price NUMERIC(20, 8),
    coincap_price NUMERIC(20, 8),
    coinpaprika_price NUMERIC(20, 8),
    coingecko_price NUMERIC(20, 8),
    
    -- 통계
    price_sources_count INTEGER,
    price_avg NUMERIC(20, 8),
    price_std_dev NUMERIC(20, 8),
    price_dispersion NUMERIC(10, 4),  -- %
    
    -- 메타데이터
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp)
);

-- ============================================
-- 2. Reddit 커뮤니티 감성 데이터 테이블
-- ============================================
CREATE TABLE IF NOT EXISTS reddit_sentiment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 언급 통계
    total_mentions INTEGER,
    positive_mentions INTEGER,
    negative_mentions INTEGER,
    neutral_mentions INTEGER,
    
    -- 서브레딧별 분석
    subreddit_breakdown JSONB,
    
    -- 감성 점수
    sentiment_score NUMERIC(10, 4),  -- -100 to 100
    community_interest NUMERIC(10, 4),  -- 0-100
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'reddit',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- ============================================
-- 3. 향상된 분산도 신호 테이블
-- ============================================
CREATE TABLE IF NOT EXISTS enhanced_dispersion_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 다중 소스 분산도
    price_dispersion NUMERIC(10, 4),
    price_sources INTEGER,
    
    -- 커뮤니티 감성
    reddit_sentiment_score NUMERIC(10, 4),
    reddit_mention_count INTEGER,
    
    -- 통합 신호
    signal_level INTEGER,  -- 1-5
    signal_type VARCHAR(20),
    confidence_score NUMERIC(10, 4),  -- 0-100
    
    -- 메타데이터
    data_sources TEXT[],
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp)
);

-- ============================================
-- 4. 인덱스 생성
-- ============================================
CREATE INDEX IF NOT EXISTS idx_multi_source_prices_crypto_time ON multi_source_prices(crypto_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_multi_source_prices_timestamp ON multi_source_prices(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_multi_source_prices_dispersion ON multi_source_prices(price_dispersion);

CREATE INDEX IF NOT EXISTS idx_reddit_sentiment_crypto_time ON reddit_sentiment(crypto_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_reddit_sentiment_timestamp ON reddit_sentiment(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_reddit_sentiment_score ON reddit_sentiment(sentiment_score);

CREATE INDEX IF NOT EXISTS idx_enhanced_signals_crypto_time ON enhanced_dispersion_signals(crypto_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_timestamp ON enhanced_dispersion_signals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_level ON enhanced_dispersion_signals(signal_level);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_type ON enhanced_dispersion_signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_enhanced_signals_confidence ON enhanced_dispersion_signals(confidence_score);

-- ============================================
-- 5. Row Level Security (RLS) 설정
-- ============================================
ALTER TABLE multi_source_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE reddit_sentiment ENABLE ROW LEVEL SECURITY;
ALTER TABLE enhanced_dispersion_signals ENABLE ROW LEVEL SECURITY;

-- 모든 사용자 읽기 허용
DROP POLICY IF EXISTS "Enable read access for all users" ON multi_source_prices;
CREATE POLICY "Enable read access for all users" ON multi_source_prices FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON reddit_sentiment;
CREATE POLICY "Enable read access for all users" ON reddit_sentiment FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON enhanced_dispersion_signals;
CREATE POLICY "Enable read access for all users" ON enhanced_dispersion_signals FOR SELECT USING (true);

-- Service role만 쓰기 허용
DROP POLICY IF EXISTS "Enable insert for service role only" ON multi_source_prices;
CREATE POLICY "Enable insert for service role only" ON multi_source_prices FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable insert for service role only" ON reddit_sentiment;
CREATE POLICY "Enable insert for service role only" ON reddit_sentiment FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable insert for service role only" ON enhanced_dispersion_signals;
CREATE POLICY "Enable insert for service role only" ON enhanced_dispersion_signals FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- Service role만 업데이트 허용
DROP POLICY IF EXISTS "Enable update for service role only" ON multi_source_prices;
CREATE POLICY "Enable update for service role only" ON multi_source_prices FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable update for service role only" ON reddit_sentiment;
CREATE POLICY "Enable update for service role only" ON reddit_sentiment FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable update for service role only" ON enhanced_dispersion_signals;
CREATE POLICY "Enable update for service role only" ON enhanced_dispersion_signals FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 6. 테이블 생성 확인
-- ============================================
SELECT 'Phase 4 스키마 생성 완료' as status;
SELECT 'multi_source_prices, reddit_sentiment, enhanced_dispersion_signals 테이블이 생성되었습니다.' as message;
