-- ============================================
-- Dispersion Signal Database Schema (Phase 3)
-- 분산도 계산 및 신호 생성
-- ============================================

-- ============================================
-- 1. 분산도 신호 테이블
-- ============================================
CREATE TABLE IF NOT EXISTS dispersion_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crypto_id UUID NOT NULL REFERENCES cryptocurrencies(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- 가격 분산도
    price_dispersion NUMERIC(10, 4), -- %
    price_sources INTEGER, -- 데이터 소스 수
    price_max NUMERIC(20, 8),
    price_min NUMERIC(20, 8),
    price_avg NUMERIC(20, 8),
    
    -- 거래량 분산도
    volume_concentration NUMERIC(10, 4), -- HHI
    volume_total NUMERIC(30, 2),
    
    -- 도미넌스 변화
    btc_dominance NUMERIC(10, 4),
    btc_dominance_change_7d NUMERIC(10, 4),
    eth_dominance NUMERIC(10, 4),
    eth_dominance_change_7d NUMERIC(10, 4),
    
    -- 신호 레벨
    signal_level INTEGER, -- 1-5 (1: 매우 낮음, 5: 매우 높음)
    signal_type VARCHAR(20), -- 'convergence', 'divergence', 'neutral'
    
    -- 메타데이터
    data_sources TEXT[],
    calculation_method VARCHAR(50),
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(crypto_id, timestamp)
);

-- ============================================
-- 2. 분산도 요약 테이블 (일일)
-- ============================================
CREATE TABLE IF NOT EXISTS dispersion_summary_daily (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    
    -- 전체 시장 분산도
    market_dispersion_avg NUMERIC(10, 4),
    market_dispersion_max NUMERIC(10, 4),
    market_dispersion_min NUMERIC(10, 4),
    
    -- 상위 코인별 분산도
    top_dispersion_coins TEXT[],
    low_dispersion_coins TEXT[],
    
    -- 도미넌스 요약
    btc_dominance_avg NUMERIC(10, 4),
    eth_dominance_avg NUMERIC(10, 4),
    
    -- 신호 통계
    high_signal_count INTEGER,
    low_signal_count INTEGER,
    
    -- 메타데이터
    coins_analyzed INTEGER,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(date)
);

-- ============================================
-- 3. 인덱스 생성
-- ============================================
CREATE INDEX IF NOT EXISTS idx_dispersion_signals_crypto_time ON dispersion_signals(crypto_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dispersion_signals_timestamp ON dispersion_signals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dispersion_signals_level ON dispersion_signals(signal_level);
CREATE INDEX IF NOT EXISTS idx_dispersion_signals_type ON dispersion_signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_dispersion_summary_date ON dispersion_summary_daily(date DESC);

-- ============================================
-- 4. Row Level Security (RLS) 설정
-- ============================================
ALTER TABLE dispersion_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE dispersion_summary_daily ENABLE ROW LEVEL SECURITY;

-- 모든 사용자 읽기 허용
DROP POLICY IF EXISTS "Enable read access for all users" ON dispersion_signals;
CREATE POLICY "Enable read access for all users" ON dispersion_signals FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON dispersion_summary_daily;
CREATE POLICY "Enable read access for all users" ON dispersion_summary_daily FOR SELECT USING (true);

-- Service role만 쓰기 허용
DROP POLICY IF EXISTS "Enable insert for service role only" ON dispersion_signals;
CREATE POLICY "Enable insert for service role only" ON dispersion_signals FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable insert for service role only" ON dispersion_summary_daily;
CREATE POLICY "Enable insert for service role only" ON dispersion_summary_daily FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- Service role만 업데이트 허용
DROP POLICY IF EXISTS "Enable update for service role only" ON dispersion_signals;
CREATE POLICY "Enable update for service role only" ON dispersion_signals FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

DROP POLICY IF EXISTS "Enable update for service role only" ON dispersion_summary_daily;
CREATE POLICY "Enable update for service role only" ON dispersion_summary_daily FOR UPDATE WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- ============================================
-- 5. 테이블 생성 확인
-- ============================================
SELECT 'Phase 3 스키마 생성 완료' as status;
SELECT 'dispersion_signals, dispersion_summary_daily 테이블이 생성되었습니다.' as message;
