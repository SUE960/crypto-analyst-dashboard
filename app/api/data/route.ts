import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { type, data } = body

    switch (type) {
      case 'coin_data':
        const { error: coinError } = await supabase
          .from('coin_data')
          .insert(data)
        
        if (coinError) throw coinError
        break

      case 'analyst_target':
        const { error: targetError } = await supabase
          .from('analyst_targets')
          .insert(data)
        
        if (targetError) throw targetError
        break

      case 'tweet_sentiment':
        const { error: tweetError } = await supabase
          .from('tweet_sentiments')
          .insert(data)
        
        if (tweetError) throw tweetError
        break

      case 'correlation_analysis':
        const { error: correlationError } = await supabase
          .from('correlation_analysis')
          .insert(data)
        
        if (correlationError) throw correlationError
        break

      default:
        return NextResponse.json(
          { error: '지원하지 않는 데이터 타입입니다.' },
          { status: 400 }
        )
    }

    return NextResponse.json({ success: true })

  } catch (error) {
    console.error('데이터 저장 에러:', error)
    return NextResponse.json(
      { error: '데이터를 저장하는 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
