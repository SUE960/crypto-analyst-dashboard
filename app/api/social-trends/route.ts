import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // 실제 환경에서는 외부 API나 데이터베이스에서 데이터를 가져옵니다
    const socialTrendsData = {
      trends: [
        {
          platform: 'Twitter',
          totalMentions: 45000,
          sentimentScore: 0.6,
          engagementRate: 0.08,
          trendingCoins: ['BTC', 'ETH', 'DOGE', 'SOL', 'ADA'],
          peakHours: ['09:00', '13:00', '20:00']
        },
        {
          platform: 'Reddit',
          totalMentions: 28000,
          sentimentScore: 0.4,
          engagementRate: 0.12,
          trendingCoins: ['BTC', 'ETH', 'DOGE', 'MATIC', 'LINK'],
          peakHours: ['10:00', '15:00', '22:00']
        },
        {
          platform: 'TikTok',
          totalMentions: 15000,
          sentimentScore: 0.8,
          engagementRate: 0.15,
          trendingCoins: ['DOGE', 'SHIB', 'PEPE', 'BTC', 'ETH'],
          peakHours: ['12:00', '18:00', '21:00']
        }
      ],
      viralContent: [
        {
          id: '1',
          platform: 'Twitter',
          coinSymbol: 'DOGE',
          coinName: 'Dogecoin',
          content: 'DOGE가 다시 달에 갈 준비가 되었다! 🚀 #Dogecoin #ToTheMoon',
          engagement: 25000,
          viralityScore: 95,
          timestamp: '2024-01-25T10:30:00Z'
        },
        {
          id: '2',
          platform: 'TikTok',
          coinSymbol: 'BTC',
          coinName: 'Bitcoin',
          content: '비트코인 투자 후 1년 후 내 포트폴리오 변화',
          engagement: 18000,
          viralityScore: 88,
          timestamp: '2024-01-25T09:15:00Z'
        },
        {
          id: '3',
          platform: 'Reddit',
          coinSymbol: 'ETH',
          coinName: 'Ethereum',
          content: '이더리움의 새로운 업그레이드가 시장에 미칠 영향 분석',
          engagement: 12000,
          viralityScore: 82,
          timestamp: '2024-01-25T08:45:00Z'
        }
      ]
    }

    return NextResponse.json({
      success: true,
      data: socialTrendsData,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('소셜 트렌드 데이터 API 오류:', error)
    return NextResponse.json(
      { success: false, error: '소셜 트렌드 데이터를 가져올 수 없습니다.' },
      { status: 500 }
    )
  }
}
