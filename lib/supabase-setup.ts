import { createClient } from '@supabase/supabase-js'

// Supabase 클라이언트 생성
const supabaseUrl = 'https://goeqmhurrhgwmazaxfpm.supabase.co'
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'your_service_role_key_here'

const supabase = createClient(supabaseUrl, supabaseKey)

// 데이터베이스 스키마 생성 함수
export async function createDatabaseSchema() {
  try {
    console.log('데이터베이스 스키마 생성 시작...')

    // 코인 데이터 테이블
    const { error: coinError } = await supabase.rpc('exec_sql', {
      sql: `
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
      `
    })

    if (coinError) {
      console.error('코인 데이터 테이블 생성 에러:', coinError)
    } else {
      console.log('✅ 코인 데이터 테이블 생성 완료')
    }

    // 애널리스트 목표가 테이블
    const { error: targetError } = await supabase.rpc('exec_sql', {
      sql: `
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
      `
    })

    if (targetError) {
      console.error('애널리스트 목표가 테이블 생성 에러:', targetError)
    } else {
      console.log('✅ 애널리스트 목표가 테이블 생성 완료')
    }

    // 트윗 감정 분석 테이블
    const { error: tweetError } = await supabase.rpc('exec_sql', {
      sql: `
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
      `
    })

    if (tweetError) {
      console.error('트윗 감정 분석 테이블 생성 에러:', tweetError)
    } else {
      console.log('✅ 트윗 감정 분석 테이블 생성 완료')
    }

    // 상관성 분석 테이블
    const { error: correlationError } = await supabase.rpc('exec_sql', {
      sql: `
        CREATE TABLE IF NOT EXISTS correlation_analysis (
          id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
          coin_symbol VARCHAR(10) NOT NULL,
          analyst_correlation DECIMAL(5, 4),
          sentiment_correlation DECIMAL(5, 4),
          price_correlation DECIMAL(5, 4),
          analysis_date DATE NOT NULL,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
      `
    })

    if (correlationError) {
      console.error('상관성 분석 테이블 생성 에러:', correlationError)
    } else {
      console.log('✅ 상관성 분석 테이블 생성 완료')
    }

    console.log('데이터베이스 스키마 생성 완료!')
    return { success: true }

  } catch (error) {
    console.error('데이터베이스 스키마 생성 에러:', error)
    return { success: false, error }
  }
}

// 인덱스 생성 함수
export async function createIndexes() {
  try {
    console.log('인덱스 생성 시작...')

    const indexes = [
      'CREATE INDEX IF NOT EXISTS idx_coin_data_symbol ON coin_data(symbol);',
      'CREATE INDEX IF NOT EXISTS idx_coin_data_created_at ON coin_data(created_at);',
      'CREATE INDEX IF NOT EXISTS idx_analyst_targets_symbol ON analyst_targets(coin_symbol);',
      'CREATE INDEX IF NOT EXISTS idx_analyst_targets_date ON analyst_targets(analysis_date);',
      'CREATE INDEX IF NOT EXISTS idx_tweet_sentiments_symbol ON tweet_sentiments(coin_symbol);',
      'CREATE INDEX IF NOT EXISTS idx_tweet_sentiments_date ON tweet_sentiments(tweet_date);',
      'CREATE INDEX IF NOT EXISTS idx_correlation_symbol ON correlation_analysis(coin_symbol);',
      'CREATE INDEX IF NOT EXISTS idx_correlation_date ON correlation_analysis(analysis_date);'
    ]

    for (const indexSql of indexes) {
      const { error } = await supabase.rpc('exec_sql', { sql: indexSql })
      if (error) {
        console.error('인덱스 생성 에러:', error)
      }
    }

    console.log('✅ 인덱스 생성 완료')
    return { success: true }

  } catch (error) {
    console.error('인덱스 생성 에러:', error)
    return { success: false, error }
  }
}

// RLS 정책 설정 함수
export async function setupRLSPolicies() {
  try {
    console.log('RLS 정책 설정 시작...')

    const policies = [
      'ALTER TABLE coin_data ENABLE ROW LEVEL SECURITY;',
      'ALTER TABLE analyst_targets ENABLE ROW LEVEL SECURITY;',
      'ALTER TABLE tweet_sentiments ENABLE ROW LEVEL SECURITY;',
      'ALTER TABLE correlation_analysis ENABLE ROW LEVEL SECURITY;',
      'CREATE POLICY "Enable read access for all users" ON coin_data FOR SELECT USING (true);',
      'CREATE POLICY "Enable read access for all users" ON analyst_targets FOR SELECT USING (true);',
      'CREATE POLICY "Enable read access for all users" ON tweet_sentiments FOR SELECT USING (true);',
      'CREATE POLICY "Enable read access for all users" ON correlation_analysis FOR SELECT USING (true);'
    ]

    for (const policySql of policies) {
      const { error } = await supabase.rpc('exec_sql', { sql: policySql })
      if (error) {
        console.error('RLS 정책 설정 에러:', error)
      }
    }

    console.log('✅ RLS 정책 설정 완료')
    return { success: true }

  } catch (error) {
    console.error('RLS 정책 설정 에러:', error)
    return { success: false, error }
  }
}
