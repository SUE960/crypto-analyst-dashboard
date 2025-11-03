-- 분석가 목표가 데이터베이스 스키마
-- 암호화폐 분석가들의 목표가, 신뢰도, 예측 정확도 등을 저장

-- 1. 분석가 프로필 테이블
CREATE TABLE analyst_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    source VARCHAR(50) NOT NULL, -- 'messari', 'digitalcoinprice', 'coinpriceforecast', 'coinness', 'upbit'
    source_id VARCHAR(100), -- 원본 소스에서의 분석가 ID
    profile_url TEXT,
    bio TEXT,
    expertise_areas TEXT[], -- ['technical', 'fundamental', 'sentiment']
    total_predictions INTEGER DEFAULT 0,
    accuracy_score DECIMAL(5,2) DEFAULT 0.00, -- 전체 정확도 점수 (0-100)
    reliability_score DECIMAL(5,2) DEFAULT 0.00, -- 신뢰도 점수 (0-100)
    followers_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 분석가 목표가 테이블
CREATE TABLE analyst_targets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    analyst_id UUID REFERENCES analyst_profiles(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    current_price DECIMAL(20,8) NOT NULL,
    target_price DECIMAL(20,8) NOT NULL,
    price_change_percent DECIMAL(8,4), -- 목표가 대비 상승률
    timeframe VARCHAR(20) NOT NULL, -- 'short_term', 'medium_term', 'long_term'
    timeframe_months INTEGER, -- 구체적인 개월 수
    analysis_type VARCHAR(20) NOT NULL, -- 'technical', 'fundamental', 'sentiment', 'mixed'
    confidence_level INTEGER CHECK (confidence_level >= 1 AND confidence_level <= 10), -- 1-10 신뢰도
    reasoning TEXT, -- 분석 근거
    key_factors TEXT[], -- 주요 요인들
    risk_factors TEXT[], -- 리스크 요인들
    source_url TEXT, -- 원본 분석 링크
    published_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE, -- 예측 유효기간
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 예측 정확도 이력 테이블
CREATE TABLE prediction_accuracy (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    analyst_id UUID REFERENCES analyst_profiles(id) ON DELETE CASCADE,
    target_id UUID REFERENCES analyst_targets(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    predicted_price DECIMAL(20,8) NOT NULL,
    actual_price DECIMAL(20,8),
    price_accuracy DECIMAL(8,4), -- 가격 정확도 (%)
    direction_accuracy BOOLEAN, -- 방향성 정확도 (상승/하락)
    timeframe VARCHAR(20) NOT NULL,
    prediction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    evaluation_date TIMESTAMP WITH TIME ZONE,
    is_evaluated BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 분석가 신뢰도 점수 이력 테이블
CREATE TABLE analyst_reliability_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    analyst_id UUID REFERENCES analyst_profiles(id) ON DELETE CASCADE,
    reliability_score DECIMAL(5,2) NOT NULL,
    accuracy_score DECIMAL(5,2) NOT NULL,
    total_predictions INTEGER NOT NULL,
    successful_predictions INTEGER NOT NULL,
    calculation_method VARCHAR(50), -- 'weighted_average', 'recent_performance', 'sector_specific'
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 코인별 분석가 목표가 집계 테이블
CREATE TABLE coin_analyst_summary (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    current_price DECIMAL(20,8) NOT NULL,
    total_analysts INTEGER DEFAULT 0,
    short_term_targets INTEGER DEFAULT 0,
    medium_term_targets INTEGER DEFAULT 0,
    long_term_targets INTEGER DEFAULT 0,
    avg_short_term_target DECIMAL(20,8),
    avg_medium_term_target DECIMAL(20,8),
    avg_long_term_target DECIMAL(20,8),
    median_short_term_target DECIMAL(20,8),
    median_medium_term_target DECIMAL(20,8),
    median_long_term_target DECIMAL(20,8),
    consensus_direction VARCHAR(10), -- 'bullish', 'bearish', 'neutral'
    confidence_level DECIMAL(5,2), -- 평균 신뢰도
    price_dispersion DECIMAL(8,4), -- 목표가 분산도
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX idx_analyst_profiles_source ON analyst_profiles(source);
CREATE INDEX idx_analyst_profiles_source_id ON analyst_profiles(source_id);
CREATE INDEX idx_analyst_targets_analyst_id ON analyst_targets(analyst_id);
CREATE INDEX idx_analyst_targets_symbol ON analyst_targets(symbol);
CREATE INDEX idx_analyst_targets_timeframe ON analyst_targets(timeframe);
CREATE INDEX idx_analyst_targets_published_at ON analyst_targets(published_at);
CREATE INDEX idx_prediction_accuracy_analyst_id ON prediction_accuracy(analyst_id);
CREATE INDEX idx_prediction_accuracy_symbol ON prediction_accuracy(symbol);
CREATE INDEX idx_prediction_accuracy_evaluation_date ON prediction_accuracy(evaluation_date);
CREATE INDEX idx_coin_analyst_summary_symbol ON coin_analyst_summary(symbol);
CREATE INDEX idx_coin_analyst_summary_last_updated ON coin_analyst_summary(last_updated);

-- RLS (Row Level Security) 정책
ALTER TABLE analyst_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyst_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE prediction_accuracy ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyst_reliability_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE coin_analyst_summary ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능
CREATE POLICY "Allow read access to analyst_profiles" ON analyst_profiles FOR SELECT USING (true);
CREATE POLICY "Allow read access to analyst_targets" ON analyst_targets FOR SELECT USING (true);
CREATE POLICY "Allow read access to prediction_accuracy" ON prediction_accuracy FOR SELECT USING (true);
CREATE POLICY "Allow read access to analyst_reliability_history" ON analyst_reliability_history FOR SELECT USING (true);
CREATE POLICY "Allow read access to coin_analyst_summary" ON coin_analyst_summary FOR SELECT USING (true);

-- 서비스 역할만 쓰기 가능
CREATE POLICY "Allow service role to insert analyst_profiles" ON analyst_profiles FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service role to update analyst_profiles" ON analyst_profiles FOR UPDATE USING (true);
CREATE POLICY "Allow service role to insert analyst_targets" ON analyst_targets FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service role to update analyst_targets" ON analyst_targets FOR UPDATE USING (true);
CREATE POLICY "Allow service role to insert prediction_accuracy" ON prediction_accuracy FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service role to update prediction_accuracy" ON prediction_accuracy FOR UPDATE USING (true);
CREATE POLICY "Allow service role to insert analyst_reliability_history" ON analyst_reliability_history FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service role to insert coin_analyst_summary" ON coin_analyst_summary FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service role to update coin_analyst_summary" ON coin_analyst_summary FOR UPDATE USING (true);

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 업데이트 트리거 적용
CREATE TRIGGER update_analyst_profiles_updated_at BEFORE UPDATE ON analyst_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_analyst_targets_updated_at BEFORE UPDATE ON analyst_targets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 코인별 분석가 목표가 집계 함수
CREATE OR REPLACE FUNCTION update_coin_analyst_summary()
RETURNS TRIGGER AS $$
BEGIN
    -- 코인별 집계 업데이트
    INSERT INTO coin_analyst_summary (
        symbol,
        current_price,
        total_analysts,
        short_term_targets,
        medium_term_targets,
        long_term_targets,
        avg_short_term_target,
        avg_medium_term_target,
        avg_long_term_target,
        median_short_term_target,
        median_medium_term_target,
        median_long_term_target,
        consensus_direction,
        confidence_level,
        price_dispersion,
        last_updated
    )
    SELECT 
        NEW.symbol,
        NEW.current_price,
        COUNT(DISTINCT analyst_id) as total_analysts,
        COUNT(CASE WHEN timeframe = 'short_term' THEN 1 END) as short_term_targets,
        COUNT(CASE WHEN timeframe = 'medium_term' THEN 1 END) as medium_term_targets,
        COUNT(CASE WHEN timeframe = 'long_term' THEN 1 END) as long_term_targets,
        AVG(CASE WHEN timeframe = 'short_term' THEN target_price END) as avg_short_term_target,
        AVG(CASE WHEN timeframe = 'medium_term' THEN target_price END) as avg_medium_term_target,
        AVG(CASE WHEN timeframe = 'long_term' THEN target_price END) as avg_long_term_target,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN timeframe = 'short_term' THEN target_price END) as median_short_term_target,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN timeframe = 'medium_term' THEN target_price END) as median_medium_term_target,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN timeframe = 'long_term' THEN target_price END) as median_long_term_target,
        CASE 
            WHEN AVG(price_change_percent) > 5 THEN 'bullish'
            WHEN AVG(price_change_percent) < -5 THEN 'bearish'
            ELSE 'neutral'
        END as consensus_direction,
        AVG(confidence_level) as confidence_level,
        STDDEV(target_price) / AVG(target_price) * 100 as price_dispersion,
        NOW() as last_updated
    FROM analyst_targets 
    WHERE symbol = NEW.symbol AND is_active = true
    ON CONFLICT (symbol) DO UPDATE SET
        current_price = EXCLUDED.current_price,
        total_analysts = EXCLUDED.total_analysts,
        short_term_targets = EXCLUDED.short_term_targets,
        medium_term_targets = EXCLUDED.medium_term_targets,
        long_term_targets = EXCLUDED.long_term_targets,
        avg_short_term_target = EXCLUDED.avg_short_term_target,
        avg_medium_term_target = EXCLUDED.avg_medium_term_target,
        avg_long_term_target = EXCLUDED.avg_long_term_target,
        median_short_term_target = EXCLUDED.median_short_term_target,
        median_medium_term_target = EXCLUDED.median_medium_term_target,
        median_long_term_target = EXCLUDED.median_long_term_target,
        consensus_direction = EXCLUDED.consensus_direction,
        confidence_level = EXCLUDED.confidence_level,
        price_dispersion = EXCLUDED.price_dispersion,
        last_updated = EXCLUDED.last_updated;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 집계 트리거 적용
CREATE TRIGGER update_coin_analyst_summary_trigger 
    AFTER INSERT OR UPDATE ON analyst_targets 
    FOR EACH ROW EXECUTE FUNCTION update_coin_analyst_summary();

-- 초기 데이터 삽입 (주요 코인들)
INSERT INTO coin_analyst_summary (symbol, current_price, total_analysts) VALUES
('BTC', 0, 0),
('ETH', 0, 0),
('SOL', 0, 0),
('XRP', 0, 0),
('BNB', 0, 0),
('DOGE', 0, 0),
('TRX', 0, 0),
('SUI', 0, 0),
('AVAX', 0, 0),
('TAO', 0, 0);

COMMENT ON TABLE analyst_profiles IS '암호화폐 분석가 프로필 정보';
COMMENT ON TABLE analyst_targets IS '분석가들의 코인별 목표가 예측';
COMMENT ON TABLE prediction_accuracy IS '분석가 예측 정확도 이력';
COMMENT ON TABLE analyst_reliability_history IS '분석가 신뢰도 점수 이력';
COMMENT ON TABLE coin_analyst_summary IS '코인별 분석가 목표가 집계';
