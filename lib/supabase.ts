import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://goeqmhurrhgwmazaxfpm.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// 데이터베이스 타입 정의
export interface CoinData {
  id: string
  symbol: string
  name: string
  current_price: number
  price_change_24h: number
  price_change_percentage_24h: number
  market_cap: number
  volume_24h: number
  created_at: string
}

export interface AnalystTarget {
  id: string
  coin_symbol: string
  analyst_name: string
  target_price: number
  current_price: number
  confidence_score: number
  analysis_date: string
  created_at: string
}

export interface TweetSentiment {
  id: string
  coin_symbol: string
  influencer_name: string
  tweet_content: string
  sentiment_score: number
  engagement_score: number
  tweet_date: string
  created_at: string
}

export interface CorrelationAnalysis {
  id: string
  coin_symbol: string
  analyst_correlation: number
  sentiment_correlation: number
  price_correlation: number
  analysis_date: string
  created_at: string
}
