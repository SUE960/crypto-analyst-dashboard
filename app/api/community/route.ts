import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // 실제 환경에서는 외부 API나 데이터베이스에서 데이터를 가져옵니다
    const communityData = {
      mentions: [
        {
          id: '1',
          platform: 'Reddit',
          coinSymbol: 'BTC',
          coinName: 'Bitcoin',
          mentionCount: 1250,
          sentimentScore: 0.6,
          engagement: 8500,
          trendingScore: 85,
          topHashtags: ['#Bitcoin', '#BTC', '#Crypto'],
          topKeywords: ['ATH', 'bullrun', 'hodl'],
          timestamp: '2024-01-25T10:00:00Z'
        },
        {
          id: '2',
          platform: 'Discord',
          coinSymbol: 'ETH',
          coinName: 'Ethereum',
          mentionCount: 980,
          sentimentScore: 0.4,
          engagement: 6200,
          trendingScore: 72,
          topHashtags: ['#Ethereum', '#ETH', '#DeFi'],
          topKeywords: ['upgrade', 'gas', 'staking'],
          timestamp: '2024-01-25T09:30:00Z'
        },
        {
          id: '3',
          platform: 'Telegram',
          coinSymbol: 'DOGE',
          coinName: 'Dogecoin',
          mentionCount: 2100,
          sentimentScore: 0.8,
          engagement: 15000,
          trendingScore: 95,
          topHashtags: ['#Dogecoin', '#DOGE', '#MemeCoin'],
          topKeywords: ['moon', 'elon', 'community'],
          timestamp: '2024-01-25T11:15:00Z'
        }
      ],
      trends: [
        { coinSymbol: 'DOGE', coinName: 'Dogecoin', totalMentions: 2100, sentimentTrend: 0.8, engagementTrend: 0.7, trendingRank: 1 },
        { coinSymbol: 'BTC', coinName: 'Bitcoin', totalMentions: 1250, sentimentTrend: 0.6, engagementTrend: 0.5, trendingRank: 2 },
        { coinSymbol: 'ETH', coinName: 'Ethereum', totalMentions: 980, sentimentTrend: 0.4, engagementTrend: 0.3, trendingRank: 3 },
        { coinSymbol: 'SOL', coinName: 'Solana', totalMentions: 750, sentimentTrend: 0.2, engagementTrend: 0.4, trendingRank: 4 },
        { coinSymbol: 'ADA', coinName: 'Cardano', totalMentions: 650, sentimentTrend: 0.3, engagementTrend: 0.2, trendingRank: 5 }
      ]
    }

    return NextResponse.json({
      success: true,
      data: communityData,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('커뮤니티 데이터 API 오류:', error)
    return NextResponse.json(
      { success: false, error: '커뮤니티 데이터를 가져올 수 없습니다.' },
      { status: 500 }
    )
  }
}
