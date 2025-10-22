-- 코인 데이터 테이블
CREATE TABLE IF NOT EXISTS coin_data (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  symbol VARCHAR(10) NOT NULL,
  name VARCHAR(100) NOT NULL,
  current_price DECIMAL(20, 8) NOT NULL,
  price_change_24h DECIMAL(20, 8),
  price_change_percentage_24h DECIMAL(10, 4),
  market_cap BIGINT,
  volume_24h BIGINT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 애널리스트 목표가 테이블
CREATE TABLE IF NOT EXISTS analyst_targets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  coin_symbol VARCHAR(10) NOT NULL,
  analyst_name VARCHAR(100) NOT NULL,
  target_price DECIMAL(20, 8) NOT NULL,
  current_price DECIMAL(20, 8) NOT NULL,
  confidence_score DECIMAL(3, 2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
  analysis_date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 트윗 감정 분석 테이블
CREATE TABLE IF NOT EXISTS tweet_sentiments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  coin_symbol VARCHAR(10) NOT NULL,
  influencer_name VARCHAR(100) NOT NULL,
  tweet_content TEXT NOT NULL,
  sentiment_score DECIMAL(3, 2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
  engagement_score INTEGER DEFAULT 0,
  tweet_date TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 상관성 분석 테이블
CREATE TABLE IF NOT EXISTS correlation_analysis (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  coin_symbol VARCHAR(10) NOT NULL,
  analyst_correlation DECIMAL(5, 4),
  sentiment_correlation DECIMAL(5, 4),
  price_correlation DECIMAL(5, 4),
  analysis_date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_coin_data_symbol ON coin_data(symbol);
CREATE INDEX IF NOT EXISTS idx_coin_data_created_at ON coin_data(created_at);
CREATE INDEX IF NOT EXISTS idx_analyst_targets_symbol ON analyst_targets(coin_symbol);
CREATE INDEX IF NOT EXISTS idx_analyst_targets_date ON analyst_targets(analysis_date);
CREATE INDEX IF NOT EXISTS idx_tweet_sentiments_symbol ON tweet_sentiments(coin_symbol);
CREATE INDEX IF NOT EXISTS idx_tweet_sentiments_date ON tweet_sentiments(tweet_date);
CREATE INDEX IF NOT EXISTS idx_correlation_symbol ON correlation_analysis(coin_symbol);
CREATE INDEX IF NOT EXISTS idx_correlation_date ON correlation_analysis(analysis_date);

-- RLS (Row Level Security) 정책 설정
ALTER TABLE coin_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyst_targets ENABLE ROW LEVEL SECURITY;
ALTER TABLE tweet_sentiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE correlation_analysis ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능하도록 설정
CREATE POLICY "Enable read access for all users" ON coin_data FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON analyst_targets FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON tweet_sentiments FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON correlation_analysis FOR SELECT USING (true);
