'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { supabase, TweetSentiment } from '@/lib/supabase'
import { MessageSquare, Heart, Repeat, TrendingUp, TrendingDown } from 'lucide-react'

export default function SentimentAnalysis() {
  const [tweets, setTweets] = useState<TweetSentiment[]>([])
  const [loading, setLoading] = useState(true)
  const [sentimentStats, setSentimentStats] = useState({
    positive: 0,
    negative: 0,
    neutral: 0,
    totalEngagement: 0
  })

  useEffect(() => {
    fetchTweetSentiments()
  }, [])

  const fetchTweetSentiments = async () => {
    try {
      const { data, error } = await supabase
        .from('tweet_sentiments')
        .select('*')
        .order('tweet_date', { ascending: false })
        .limit(50)

      if (error) throw error
      
      setTweets(data || [])
      
      // 감정 통계 계산
      const stats = data?.reduce((acc, tweet) => {
        if (tweet.sentiment_score > 0.1) acc.positive++
        else if (tweet.sentiment_score < -0.1) acc.negative++
        else acc.neutral++
        
        acc.totalEngagement += tweet.engagement_score
        return acc
      }, { positive: 0, negative: 0, neutral: 0, totalEngagement: 0 }) || { positive: 0, negative: 0, neutral: 0, totalEngagement: 0 }
      
      setSentimentStats(stats)
    } catch (error) {
      console.error('트윗 감정 분석 로딩 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (score: number) => {
    if (score > 0.1) return 'text-green-500'
    if (score < -0.1) return 'text-red-500'
    return 'text-yellow-500'
  }

  const getSentimentIcon = (score: number) => {
    if (score > 0.1) return <TrendingUp className="h-4 w-4" />
    if (score < -0.1) return <TrendingDown className="h-4 w-4" />
    return <MessageSquare className="h-4 w-4" />
  }

  const getSentimentText = (score: number) => {
    if (score > 0.1) return '긍정적'
    if (score < -0.1) return '부정적'
    return '중립적'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 감정 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              <div>
                <div className="text-sm text-muted-foreground">긍정적</div>
                <div className="text-lg font-semibold text-green-500">{sentimentStats.positive}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingDown className="h-4 w-4 text-red-500" />
              <div>
                <div className="text-sm text-muted-foreground">부정적</div>
                <div className="text-lg font-semibold text-red-500">{sentimentStats.negative}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-4 w-4 text-yellow-500" />
              <div>
                <div className="text-sm text-muted-foreground">중립적</div>
                <div className="text-lg font-semibold text-yellow-500">{sentimentStats.neutral}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Heart className="h-4 w-4 text-primary" />
              <div>
                <div className="text-sm text-muted-foreground">총 참여도</div>
                <div className="text-lg font-semibold">{sentimentStats.totalEngagement.toLocaleString()}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 트윗 목록 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">최근 트윗 분석</h3>
        {tweets.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            트윗 감정 분석 데이터가 없습니다.
          </div>
        ) : (
          tweets.map((tweet) => (
            <Card key={tweet.id} className="hover:bg-accent/50 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">{tweet.coin_symbol}</span>
                      <span className="text-sm text-muted-foreground">by {tweet.influencer_name}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className={`flex items-center space-x-1 ${getSentimentColor(tweet.sentiment_score)}`}>
                      {getSentimentIcon(tweet.sentiment_score)}
                      <span className="text-sm font-medium">{getSentimentText(tweet.sentiment_score)}</span>
                    </div>
                    
                    <div className="text-sm text-muted-foreground">
                      참여도: {tweet.engagement_score.toLocaleString()}
                    </div>
                  </div>
                </div>
                
                <div className="text-sm mb-3 p-3 bg-muted/50 rounded-md">
                  "{tweet.tweet_content}"
                </div>
                
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>트윗일: {new Date(tweet.tweet_date).toLocaleDateString('ko-KR')}</span>
                  <span>감정 점수: {tweet.sentiment_score.toFixed(2)}</span>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
