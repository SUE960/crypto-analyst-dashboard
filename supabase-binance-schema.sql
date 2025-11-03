-- ============================================
-- Dispersion Signal Database Schema (Binance API 버전)
-- 실제 Binance API 응답 구조 기반 설계
-- ============================================

-- ============================================
-- 1. 코인 마스터 테이블 (Binance 심볼 포함)
-- ============================================
CREATE TABLE IF NOT EXISTS cryptocurrencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL UNIQUE, -- BTC, ETH, SOL
    name VARCHAR(100) NOT NULL, -- Bitcoin, Ethereum
    binance_symbol VARCHAR(20), -- BTCUSDT, ETHUSDT
    market_cap_rank INTEGER, -- 시가총액 순위
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_crypto_symbol ON cryptocurrencies(symbol);
CREATE INDEX IF NOT EXISTS idx_crypto_binance_symbol ON cryptocurrencies(binance_symbol);
CREATE INDEX IF NOT EXISTS idx_crypto_active ON cryptocurrencies(is_active);
CREATE INDEX IF NOT EXISTS idx_crypto_market_cap_rank ON cryptocurrencies(market_cap_rank);

-- ============================================
-- 2. 일일 시장 데이터 테이블 (24시간 데이터)
-- ============================================
CREATE TABLE IF NOT EXISTS market_data_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    date DATE NOT NULL, -- 날짜 (YYYY-MM-DD)
    
    -- OHLCV 데이터
    open_price NUMERIC(20, 8) NOT NULL, -- 시가
    high_price NUMERIC(20, 8) NOT NULL, -- 고가
    low_price NUMERIC(20, 8) NOT NULL, -- 저가
    close_price NUMERIC(20, 8) NOT NULL, -- 종가
    volume NUMERIC(20, 8) NOT NULL, -- 거래량 (코인 단위)
    quote_volume NUMERIC(20, 2) NOT NULL, -- 거래량 (USDT 단위)
    
    -- 가격 변화
    price_change_24h NUMERIC(20, 8), -- 24시간 가격 변화
    price_change_percent_24h NUMERIC(10, 4), -- 24시간 가격 변화율 (%)
    
    -- 추가 메트릭
    weighted_avg_price NUMERIC(20, 8), -- 가중평균가격
    prev_close_price NUMERIC(20, 8), -- 전일 종가
    last_price NUMERIC(20, 8), -- 최종 가격
    bid_price NUMERIC(20, 8), -- 매수 가격
    ask_price NUMERIC(20, 8), -- 매도 가격
    
    -- 거래 통계
    trade_count INTEGER, -- 거래 수
    first_trade_id BIGINT, -- 첫 거래 ID
    last_trade_id BIGINT, -- 마지막 거래 ID
    
    -- 시간 정보
    open_time TIMESTAMPTZ, -- 시작 시간
    close_time TIMESTAMPTZ, -- 종료 시간
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'binance',
    raw_data JSONB, -- 원본 API 응답 저장
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, date, data_source)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_market_crypto_date ON market_data_daily(crypto_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_market_date ON market_data_daily(date DESC);
CREATE INDEX IF NOT EXISTS idx_market_volume ON market_data_daily(quote_volume DESC);

-- ============================================
-- 3. 히스토리컬 가격 데이터 테이블 (일일 캔들)
-- ============================================
CREATE TABLE IF NOT EXISTS price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL, -- 캔들 시작 시간
    
    -- OHLCV 데이터
    open_price NUMERIC(20, 8) NOT NULL,
    high_price NUMERIC(20, 8) NOT NULL,
    low_price NUMERIC(20, 8) NOT NULL,
    close_price NUMERIC(20, 8) NOT NULL,
    volume NUMERIC(20, 8) NOT NULL,
    quote_volume NUMERIC(20, 2) NOT NULL,
    
    -- 거래 통계
    trade_count INTEGER,
    taker_buy_volume NUMERIC(20, 8), -- 매수 거래량
    taker_buy_quote_volume NUMERIC(20, 2), -- 매수 거래량 (USDT)
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'binance',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_price_crypto_time ON price_history(crypto_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_history(timestamp DESC);

-- ============================================
-- 4. 현재 가격 테이블 (실시간 가격)
-- ============================================
CREATE TABLE IF NOT EXISTS current_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 가격 정보
    price NUMERIC(20, 8) NOT NULL, -- 현재 가격
    
    -- 메타데이터
    data_source VARCHAR(50) DEFAULT 'binance',
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp, data_source)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_current_crypto_time ON current_prices(crypto_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_current_timestamp ON current_prices(timestamp DESC);

-- ============================================
-- 5. Row Level Security (RLS) 설정
-- ============================================
ALTER TABLE cryptocurrencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_data_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE current_prices ENABLE ROW LEVEL SECURITY;

-- 모든 사용자 읽기 허용
DROP POLICY IF EXISTS "Enable read access for all users" ON cryptocurrencies;
CREATE POLICY "Enable read access for all users" ON cryptocurrencies FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON market_data_daily;
CREATE POLICY "Enable read access for all users" ON market_data_daily FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON price_history;
CREATE POLICY "Enable read access for all users" ON price_history FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON current_prices;
CREATE POLICY "Enable read access for all users" ON current_prices FOR SELECT USING (true);

-- Service role만 쓰기 허용
DROP POLICY IF EXISTS "Enable insert for service role only" ON cryptocurrencies;
CREATE POLICY "Enable insert for service role only" ON cryptocurrencies FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable insert for service role only" ON market_data_daily;
CREATE POLICY "Enable insert for service role only" ON market_data_daily FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable insert for service role only" ON price_history;
CREATE POLICY "Enable insert for service role only" ON price_history FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable insert for service role only" ON current_prices;
CREATE POLICY "Enable insert for service role only" ON current_prices FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- Service role만 업데이트 허용
DROP POLICY IF EXISTS "Enable update for service role only" ON cryptocurrencies;
CREATE POLICY "Enable update for service role only" ON cryptocurrencies FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable update for service role only" ON market_data_daily;
CREATE POLICY "Enable update for service role only" ON market_data_daily FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable update for service role only" ON price_history;
CREATE POLICY "Enable update for service role only" ON price_history FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable update for service role only" ON current_prices;
CREATE POLICY "Enable update for service role only" ON current_prices FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 6. 기본 데이터 삽입 (상위 20개 코인)
-- ============================================
INSERT INTO cryptocurrencies (symbol, name, binance_symbol, market_cap_rank) VALUES
('BTC', 'Bitcoin', 'BTCUSDT', 1),
('ETH', 'Ethereum', 'ETHUSDT', 2),
('USDC', 'USD Coin', 'USDCUSDT', 3),
('SOL', 'Solana', 'SOLUSDT', 4),
('XRP', 'Ripple', 'XRPUSDT', 5),
('BNB', 'BNB', 'BNBUSDT', 6),
('ZEC', 'Zcash', 'ZECUSDT', 7),
('FDUSD', 'First Digital USD', 'FDUSDUSDT', 8),
('GIGGLE', 'Giggle', 'GIGGLEUSDT', 9),
('DOGE', 'Dogecoin', 'DOGEUSDT', 10),
('VIRTUAL', 'Virtual', 'VIRTUALUSDT', 11),
('ASTER', 'Aster', 'ASTERUSDT', 12),
('TRX', 'TRON', 'TRXUSDT', 13),
('SUI', 'Sui', 'SUIUSDT', 14),
('AIXBT', 'AIXBT', 'AIXBTUSDT', 15),
('USDE', 'USDE', 'USDEUSDT', 16),
('XPL', 'XPL', 'XPLUSDT', 17),
('PUMP', 'Pump', 'PUMPUSDT', 18),
('TAO', 'Bittensor', 'TAOUSDT', 19),
('AVAX', 'Avalanche', 'AVAXUSDT', 20)
ON CONFLICT (symbol) DO UPDATE SET
    binance_symbol = EXCLUDED.binance_symbol,
    market_cap_rank = EXCLUDED.market_cap_rank,
    updated_at = NOW();

-- ============================================
-- 7. 테이블 생성 확인
-- ============================================
SELECT 'Binance API 스키마 생성 완료' as status;
SELECT symbol, name, binance_symbol, market_cap_rank FROM cryptocurrencies ORDER BY market_cap_rank LIMIT 10;
