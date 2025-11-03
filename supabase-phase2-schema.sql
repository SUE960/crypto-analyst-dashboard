-- ============================================
-- Dispersion Signal Database Schema (Phase 2)
-- CoinMarketCap & CryptoCompare API 통합
-- ============================================

-- ============================================
-- 1. 시가총액 데이터 테이블
-- ============================================
CREATE TABLE IF NOT EXISTS market_cap_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 시가총액 정보
    market_cap NUMERIC(30, 2),
    market_cap_rank INTEGER,
    fully_diluted_market_cap NUMERIC(30, 2),
    
    -- 공급량 정보
    circulating_supply NUMERIC(30, 8),
    total_supply NUMERIC(30, 8),
    max_supply NUMERIC(30, 8),
    
    -- 도미넌스
    market_cap_dominance NUMERIC(10, 4),
    
    -- ATH/ATL
    ath_price NUMERIC(20, 8),
    ath_date TIMESTAMPTZ,
    ath_change_percentage NUMERIC(10, 4),
    atl_price NUMERIC(20, 8),
    atl_date TIMESTAMPTZ,
    atl_change_percentage NUMERIC(10, 4),
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'coinmarketcap',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- ============================================
-- 2. 소셜 데이터 테이블
-- ============================================
CREATE TABLE IF NOT EXISTS social_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 트위터 데이터
    twitter_followers INTEGER,
    twitter_following INTEGER,
    twitter_lists INTEGER,
    twitter_favourites INTEGER,
    twitter_statuses INTEGER,
    
    -- 레딧 데이터
    reddit_subscribers INTEGER,
    reddit_active_users INTEGER,
    reddit_posts_per_hour NUMERIC(10, 2),
    reddit_comments_per_hour NUMERIC(10, 2),
    
    -- 커뮤니티 데이터
    community_score NUMERIC(10, 2),
    public_interest_score NUMERIC(10, 2),
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'cryptocompare',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- ============================================
-- 3. 뉴스 및 감성 데이터 테이블
-- ============================================
CREATE TABLE IF NOT EXISTS news_sentiment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 뉴스 정보
    news_count INTEGER,
    news_sources TEXT[],
    
    -- 감성 분석
    sentiment_score NUMERIC(5, 2), -- -100 to 100
    sentiment_positive INTEGER,
    sentiment_neutral INTEGER,
    sentiment_negative INTEGER,
    
    -- 트렌드
    trending_score NUMERIC(10, 2),
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'cryptocompare',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- ============================================
-- 4. 글로벌 메트릭 테이블
-- ============================================
CREATE TABLE IF NOT EXISTS global_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 전체 시장 데이터
    total_market_cap NUMERIC(30, 2),
    total_volume_24h NUMERIC(30, 2),
    btc_dominance NUMERIC(10, 4),
    eth_dominance NUMERIC(10, 4),
    active_cryptocurrencies INTEGER,
    active_exchanges INTEGER,
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'coinmarketcap',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(timestamp, data_source)
);

-- ============================================
-- 5. 인덱스 생성
-- ============================================
CREATE INDEX IF NOT EXISTS idx_market_cap_crypto_time ON market_cap_data(crypto_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_market_cap_timestamp ON market_cap_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_market_cap_rank ON market_cap_data(market_cap_rank);

CREATE INDEX IF NOT EXISTS idx_social_crypto_time ON social_data(crypto_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_social_timestamp ON social_data(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_news_crypto_time ON news_sentiment(crypto_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_news_timestamp ON news_sentiment(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_news_sentiment_score ON news_sentiment(sentiment_score);

CREATE INDEX IF NOT EXISTS idx_global_time ON global_metrics(timestamp DESC);

-- ============================================
-- 6. Row Level Security (RLS) 설정
-- ============================================
ALTER TABLE market_cap_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE news_sentiment ENABLE ROW LEVEL SECURITY;
ALTER TABLE global_metrics ENABLE ROW LEVEL SECURITY;

-- 모든 사용자 읽기 허용
DROP POLICY IF EXISTS "Enable read access for all users" ON market_cap_data;
CREATE POLICY "Enable read access for all users" ON market_cap_data FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON social_data;
CREATE POLICY "Enable read access for all users" ON social_data FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON news_sentiment;
CREATE POLICY "Enable read access for all users" ON news_sentiment FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON global_metrics;
CREATE POLICY "Enable read access for all users" ON global_metrics FOR SELECT USING (true);

-- Service role만 쓰기 허용
DROP POLICY IF EXISTS "Enable insert for service role only" ON market_cap_data;
CREATE POLICY "Enable insert for service role only" ON market_cap_data FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable insert for service role only" ON social_data;
CREATE POLICY "Enable insert for service role only" ON social_data FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable insert for service role only" ON news_sentiment;
CREATE POLICY "Enable insert for service role only" ON news_sentiment FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable insert for service role only" ON global_metrics;
CREATE POLICY "Enable insert for service role only" ON global_metrics FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- Service role만 업데이트 허용
DROP POLICY IF EXISTS "Enable update for service role only" ON market_cap_data;
CREATE POLICY "Enable update for service role only" ON market_cap_data FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable update for service role only" ON social_data;
CREATE POLICY "Enable update for service role only" ON social_data FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable update for service role only" ON news_sentiment;
CREATE POLICY "Enable update for service role only" ON news_sentiment FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable update for service role only" ON global_metrics;
CREATE POLICY "Enable update for service role only" ON global_metrics FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 7. 테이블 생성 확인
-- ============================================
SELECT 'Phase 2 스키마 생성 완료' as status;
SELECT 'market_cap_data, social_data, news_sentiment, global_metrics 테이블이 생성되었습니다.' as message;
