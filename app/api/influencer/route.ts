import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    // 실제 환경에서는 외부 API나 데이터베이스에서 데이터를 가져옵니다
    const influencerMentions = [
      {
        id: '1',
        influencerName: 'CryptoWhale',
        platform: 'Twitter',
        coinSymbol: 'BTC',
        coinName: 'Bitcoin',
        mentionType: 'positive',
        sentimentScore: 0.8,
        reach: 150000,
        engagement: 2500,
        timestamp: '2024-01-25T10:30:00Z',
        content: 'Bitcoin이 새로운 ATH를 기록할 준비가 되었다고 생각합니다. 기술적 분석상 매우 긍정적입니다.'
      },
      {
        id: '2',
        influencerName: 'DeFiExpert',
        platform: 'YouTube',
        coinSymbol: 'ETH',
        coinName: 'Ethereum',
        mentionType: 'positive',
        sentimentScore: 0.7,
        reach: 80000,
        engagement: 1200,
        timestamp: '2024-01-25T09:15:00Z',
        content: '이더리움의 새로운 업그레이드가 시장에 긍정적인 영향을 미칠 것으로 예상됩니다.'
      },
      {
        id: '3',
        influencerName: 'CryptoBear',
        platform: 'Telegram',
        coinSymbol: 'SOL',
        coinName: 'Solana',
        mentionType: 'negative',
        sentimentScore: -0.6,
        reach: 45000,
        engagement: 800,
        timestamp: '2024-01-25T08:45:00Z',
        content: '솔라나의 네트워크 문제가 계속 발생하고 있어 우려스럽습니다.'
      }
    ]

    return NextResponse.json({
      success: true,
      data: influencerMentions,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('인플루언서 데이터 API 오류:', error)
    return NextResponse.json(
      { success: false, error: '인플루언서 데이터를 가져올 수 없습니다.' },
      { status: 500 }
    )
  }
}
