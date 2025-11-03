-- ============================================
-- Dispersion Signal - 간단한 테스트용 스키마
-- ============================================

-- 1. 코인 마스터 테이블 (간단 버전)
CREATE TABLE IF NOT EXISTS cryptocurrencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    coingecko_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_crypto_symbol ON cryptocurrencies(symbol);
CREATE INDEX IF NOT EXISTS idx_crypto_active ON cryptocurrencies(is_active);

-- 2. 기본 데이터 삽입
INSERT INTO cryptocurrencies (symbol, name, coingecko_id) VALUES
('BTC', 'Bitcoin', 'bitcoin'),
('ETH', 'Ethereum', 'ethereum'),
('SOL', 'Solana', 'solana'),
('XRP', 'Ripple', 'ripple'),
('BNB', 'BNB', 'binancecoin')
ON CONFLICT (symbol) DO NOTHING;

-- 3. Row Level Security 설정
ALTER TABLE cryptocurrencies ENABLE ROW LEVEL SECURITY;

-- 모든 사용자 읽기 허용
DROP POLICY IF EXISTS "Enable read access for all users" ON cryptocurrencies;
CREATE POLICY "Enable read access for all users" ON cryptocurrencies FOR SELECT USING (true);

-- Service role만 쓰기 허용
DROP POLICY IF EXISTS "Enable insert for service role only" ON cryptocurrencies;
CREATE POLICY "Enable insert for service role only" ON cryptocurrencies FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- 4. 테이블 확인
SELECT 'cryptocurrencies 테이블 생성 완료' as status;
SELECT symbol, name, coingecko_id FROM cryptocurrencies ORDER BY symbol;
