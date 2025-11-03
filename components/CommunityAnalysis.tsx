'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, TrendingDown, Users, MessageSquare, Hash, Heart, ThumbsUp } from 'lucide-react'

interface CommunityMention {
  id: string
  platform: string
  coinSymbol: string
  coinName: string
  mentionCount: number
  sentimentScore: number
  engagement: number
  trendingScore: number
  topHashtags: string[]
  topKeywords: string[]
  timestamp: string
}

interface CommunityTrend {
  coinSymbol: string
  coinName: string
  totalMentions: number
  sentimentTrend: number
  engagementTrend: number
  trendingRank: number
}

export default function CommunityAnalysis() {
  const [mentions, setMentions] = useState<CommunityMention[]>([])
  const [trends, setTrends] = useState<CommunityTrend[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCommunityData()
  }, [])

  const fetchCommunityData = async () => {
    try {
      // 샘플 데이터
      const sampleMentions: CommunityMention[] = [
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
      ]

      const sampleTrends: CommunityTrend[] = [
        { coinSymbol: 'DOGE', coinName: 'Dogecoin', totalMentions: 2100, sentimentTrend: 0.8, engagementTrend: 0.7, trendingRank: 1 },
        { coinSymbol: 'BTC', coinName: 'Bitcoin', totalMentions: 1250, sentimentTrend: 0.6, engagementTrend: 0.5, trendingRank: 2 },
        { coinSymbol: 'ETH', coinName: 'Ethereum', totalMentions: 980, sentimentTrend: 0.4, engagementTrend: 0.3, trendingRank: 3 },
        { coinSymbol: 'SOL', coinName: 'Solana', totalMentions: 750, sentimentTrend: 0.2, engagementTrend: 0.4, trendingRank: 4 },
        { coinSymbol: 'ADA', coinName: 'Cardano', totalMentions: 650, sentimentTrend: 0.3, engagementTrend: 0.2, trendingRank: 5 }
      ]
      
      setMentions(sampleMentions)
      setTrends(sampleTrends)
    } catch (error) {
      console.error('커뮤니티 데이터 로딩 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return 'text-green-600'
    if (score < -0.3) return 'text-red-600'
    return 'text-gray-600'
  }

  const getTrendingColor = (score: number) => {
    if (score > 80) return 'text-red-500'
    if (score > 60) return 'text-orange-500'
    return 'text-gray-500'
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Users className="h-5 w-5 mr-2" />
            커뮤니티 언급 분석
          </CardTitle>
          <CardDescription>Reddit, Discord, Telegram 등 커뮤니티 언급 현황</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* 커뮤니티 트렌드 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            커뮤니티 트렌드 TOP 5
          </CardTitle>
          <CardDescription>가장 많이 언급되고 있는 암호화폐</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {trends.map((trend, index) => (
              <div key={trend.coinSymbol} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-blue-600">#{trend.trendingRank}</span>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{trend.coinName}</h4>
                    <p className="text-sm text-gray-500">{trend.coinSymbol}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4 text-sm">
                  <span className="text-gray-600">{trend.totalMentions.toLocaleString()} 언급</span>
                  <span className={`${getSentimentColor(trend.sentimentTrend)}`}>
                    감정: {(trend.sentimentTrend * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 플랫폼별 상세 분석 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageSquare className="h-5 w-5 mr-2" />
            플랫폼별 상세 분석
          </CardTitle>
          <CardDescription>각 플랫폼에서의 코인별 언급 현황</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mentions.map((mention) => (
              <div key={mention.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <Hash className="h-4 w-4 text-purple-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{mention.platform}</h4>
                      <p className="text-sm text-gray-500">{mention.coinName} ({mention.coinSymbol})</p>
                    </div>
                  </div>
                  <div className={`text-sm font-medium ${getTrendingColor(mention.trendingScore)}`}>
                    트렌딩: {mention.trendingScore}점
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 mb-3">
                  <div className="text-center">
                    <div className="text-lg font-bold text-gray-900">{mention.mentionCount.toLocaleString()}</div>
                    <div className="text-xs text-gray-500">언급 수</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-lg font-bold ${getSentimentColor(mention.sentimentScore)}`}>
                      {(mention.sentimentScore * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-500">감정 점수</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-gray-900">{mention.engagement.toLocaleString()}</div>
                    <div className="text-xs text-gray-500">참여도</div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div>
                    <span className="text-xs font-medium text-gray-600">인기 해시태그:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {mention.topHashtags.map((tag, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-gray-600">핵심 키워드:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {mention.topKeywords.map((keyword, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
