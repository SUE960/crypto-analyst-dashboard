import { supabase } from '@/lib/supabase'

// 샘플 코인 데이터
const sampleCoins = [
  { symbol: 'BTC', name: 'Bitcoin', current_price: 45000, price_change_24h: 1200, price_change_percentage_24h: 2.74, market_cap: 850000000000, volume_24h: 25000000000 },
  { symbol: 'ETH', name: 'Ethereum', current_price: 3200, price_change_24h: -80, price_change_percentage_24h: -2.44, market_cap: 380000000000, volume_24h: 15000000000 },
  { symbol: 'ADA', name: 'Cardano', current_price: 0.45, price_change_24h: 0.02, price_change_percentage_24h: 4.65, market_cap: 15000000000, volume_24h: 800000000 },
  { symbol: 'SOL', name: 'Solana', current_price: 95, price_change_24h: 3.5, price_change_percentage_24h: 3.82, market_cap: 40000000000, volume_24h: 2000000000 },
  { symbol: 'DOT', name: 'Polkadot', current_price: 6.8, price_change_24h: -0.2, price_change_percentage_24h: -2.86, market_cap: 8000000000, volume_24h: 400000000 }
]

// 샘플 애널리스트 목표가
const sampleTargets = [
  { coin_symbol: 'BTC', analyst_name: 'CryptoAnalyst_Pro', target_price: 50000, current_price: 45000, confidence_score: 0.85, analysis_date: '2024-01-15' },
  { coin_symbol: 'BTC', analyst_name: 'BitcoinExpert', target_price: 48000, current_price: 45000, confidence_score: 0.78, analysis_date: '2024-01-14' },
  { coin_symbol: 'ETH', analyst_name: 'EthereumInsider', target_price: 3500, current_price: 3200, confidence_score: 0.82, analysis_date: '2024-01-15' },
  { coin_symbol: 'ETH', analyst_name: 'CryptoGuru', target_price: 3400, current_price: 3200, confidence_score: 0.75, analysis_date: '2024-01-14' },
  { coin_symbol: 'ADA', analyst_name: 'CardanoAnalyst', target_price: 0.55, current_price: 0.45, confidence_score: 0.88, analysis_date: '2024-01-15' },
  { coin_symbol: 'SOL', analyst_name: 'SolanaExpert', target_price: 110, current_price: 95, confidence_score: 0.80, analysis_date: '2024-01-15' },
  { coin_symbol: 'DOT', analyst_name: 'PolkadotPro', target_price: 8.5, current_price: 6.8, confidence_score: 0.77, analysis_date: '2024-01-15' }
]

// 샘플 트윗 감정 분석
const sampleTweets = [
  { coin_symbol: 'BTC', influencer_name: 'CryptoWhale', tweet_content: 'Bitcoin is showing strong bullish momentum! 🚀 The recent breakout above $45k is just the beginning.', sentiment_score: 0.8, engagement_score: 15420, tweet_date: '2024-01-15T10:30:00Z' },
  { coin_symbol: 'BTC', influencer_name: 'BitcoinMaxi', tweet_content: 'HODL! Bitcoin will reach $100k by end of year. The fundamentals are stronger than ever.', sentiment_score: 0.9, engagement_score: 8930, tweet_date: '2024-01-15T09:15:00Z' },
  { coin_symbol: 'ETH', influencer_name: 'EthereumDev', tweet_content: 'Ethereum 2.0 upgrades are progressing well. The merge was successful and we\'re seeing improved efficiency.', sentiment_score: 0.7, engagement_score: 12350, tweet_date: '2024-01-15T11:00:00Z' },
  { coin_symbol: 'ETH', influencer_name: 'CryptoCritic', tweet_content: 'Ethereum gas fees are still too high for regular users. Need more scaling solutions.', sentiment_score: -0.3, engagement_score: 5670, tweet_date: '2024-01-15T08:45:00Z' },
  { coin_symbol: 'ADA', influencer_name: 'CardanoFan', tweet_content: 'Cardano\'s smart contract capabilities are finally here! Exciting times ahead for ADA holders.', sentiment_score: 0.6, engagement_score: 7890, tweet_date: '2024-01-15T12:20:00Z' },
  { coin_symbol: 'SOL', influencer_name: 'SolanaBuilder', tweet_content: 'Solana\'s speed and low fees make it the perfect platform for DeFi applications.', sentiment_score: 0.8, engagement_score: 11200, tweet_date: '2024-01-15T13:10:00Z' },
  { coin_symbol: 'DOT', influencer_name: 'PolkadotEco', tweet_content: 'Polkadot\'s parachain auctions are bringing innovative projects to the ecosystem.', sentiment_score: 0.5, engagement_score: 4450, tweet_date: '2024-01-15T14:30:00Z' }
]

// 샘플 상관성 분석
const sampleCorrelations = [
  { coin_symbol: 'BTC', analyst_correlation: 0.75, sentiment_correlation: 0.68, price_correlation: 0.82, analysis_date: '2024-01-15' },
  { coin_symbol: 'ETH', analyst_correlation: 0.72, sentiment_correlation: 0.61, price_correlation: 0.78, analysis_date: '2024-01-15' },
  { coin_symbol: 'ADA', analyst_correlation: 0.68, sentiment_correlation: 0.55, price_correlation: 0.71, analysis_date: '2024-01-15' },
  { coin_symbol: 'SOL', analyst_correlation: 0.71, sentiment_correlation: 0.63, price_correlation: 0.76, analysis_date: '2024-01-15' },
  { coin_symbol: 'DOT', analyst_correlation: 0.66, sentiment_correlation: 0.48, price_correlation: 0.69, analysis_date: '2024-01-15' }
]

export async function seedDatabase() {
  try {
    console.log('데이터베이스 시딩 시작...')

    // 코인 데이터 삽입
    for (const coin of sampleCoins) {
      const { error } = await supabase
        .from('coin_data')
        .insert(coin)
      
      if (error) {
        console.error('코인 데이터 삽입 에러:', error)
      } else {
        console.log(`${coin.symbol} 데이터 삽입 완료`)
      }
    }

    // 애널리스트 목표가 삽입
    for (const target of sampleTargets) {
      const { error } = await supabase
        .from('analyst_targets')
        .insert(target)
      
      if (error) {
        console.error('애널리스트 목표가 삽입 에러:', error)
      } else {
        console.log(`${target.coin_symbol} 목표가 삽입 완료`)
      }
    }

    // 트윗 감정 분석 삽입
    for (const tweet of sampleTweets) {
      const { error } = await supabase
        .from('tweet_sentiments')
        .insert(tweet)
      
      if (error) {
        console.error('트윗 감정 분석 삽입 에러:', error)
      } else {
        console.log(`${tweet.coin_symbol} 트윗 삽입 완료`)
      }
    }

    // 상관성 분석 삽입
    for (const correlation of sampleCorrelations) {
      const { error } = await supabase
        .from('correlation_analysis')
        .insert(correlation)
      
      if (error) {
        console.error('상관성 분석 삽입 에러:', error)
      } else {
        console.log(`${correlation.coin_symbol} 상관성 분석 삽입 완료`)
      }
    }

    console.log('데이터베이스 시딩 완료!')
    return { success: true }

  } catch (error) {
    console.error('데이터베이스 시딩 에러:', error)
    return { success: false, error }
  }
}
