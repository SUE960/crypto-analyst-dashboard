import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const symbol = searchParams.get('symbol') || 'BTC'
    
    // 코인 데이터 가져오기
    const { data: coins, error: coinsError } = await supabase
      .from('coin_data')
      .select('*')
      .eq('symbol', symbol)
      .order('created_at', { ascending: false })
      .limit(1)

    if (coinsError) throw coinsError

    // 애널리스트 목표가 가져오기
    const { data: targets, error: targetsError } = await supabase
      .from('analyst_targets')
      .select('*')
      .eq('coin_symbol', symbol)
      .order('analysis_date', { ascending: false })
      .limit(10)

    if (targetsError) throw targetsError

    // 트윗 감정 분석 가져오기
    const { data: tweets, error: tweetsError } = await supabase
      .from('tweet_sentiments')
      .select('*')
      .eq('coin_symbol', symbol)
      .order('tweet_date', { ascending: false })
      .limit(20)

    if (tweetsError) throw tweetsError

    // 상관성 분석 가져오기
    const { data: correlations, error: correlationsError } = await supabase
      .from('correlation_analysis')
      .select('*')
      .eq('coin_symbol', symbol)
      .order('analysis_date', { ascending: false })
      .limit(1)

    if (correlationsError) throw correlationsError

    return NextResponse.json({
      coin: coins?.[0] || null,
      targets: targets || [],
      tweets: tweets || [],
      correlation: correlations?.[0] || null
    })

  } catch (error) {
    console.error('API 에러:', error)
    return NextResponse.json(
      { error: '데이터를 가져오는 중 오류가 발생했습니다.' },
      { status: 500 }
    )
  }
}
