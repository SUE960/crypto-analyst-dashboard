'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, TrendingDown, BarChart3, Activity, Zap, Target } from 'lucide-react'

interface SocialTrend {
  platform: string
  totalMentions: number
  sentimentScore: number
  engagementRate: number
  trendingCoins: string[]
  peakHours: string[]
}

interface ViralContent {
  id: string
  platform: string
  coinSymbol: string
  coinName: string
  content: string
  engagement: number
  viralityScore: number
  timestamp: string
}

export default function SocialTrendsAnalysis() {
  const [trends, setTrends] = useState<SocialTrend[]>([])
  const [viralContent, setViralContent] = useState<ViralContent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSocialTrends()
  }, [])

  const fetchSocialTrends = async () => {
    try {
      const sampleTrends: SocialTrend[] = [
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
      ]

      const sampleViralContent: ViralContent[] = [
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
      
      setTrends(sampleTrends)
      setViralContent(sampleViralContent)
    } catch (error) {
      console.error('소셜 트렌드 데이터 로딩 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (score: number) => {
    if (score > 0.5) return 'text-green-600'
    if (score > 0.2) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getViralityColor = (score: number) => {
    if (score > 90) return 'text-red-500'
    if (score > 70) return 'text-orange-500'
    return 'text-blue-500'
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            소셜 미디어 트렌드 분석
          </CardTitle>
          <CardDescription>전체 소셜 미디어 플랫폼의 암호화폐 트렌드</CardDescription>
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
      {/* 플랫폼별 트렌드 요약 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            플랫폼별 트렌드 요약
          </CardTitle>
          <CardDescription>각 플랫폼의 전체적인 암호화폐 언급 현황</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {trends.map((trend, index) => (
              <div key={trend.platform} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">{trend.platform}</h4>
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Activity className="h-4 w-4 text-blue-600" />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">총 언급:</span>
                    <span className="font-medium">{trend.totalMentions.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">감정 점수:</span>
                    <span className={`font-medium ${getSentimentColor(trend.sentimentScore)}`}>
                      {(trend.sentimentScore * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">참여율:</span>
                    <span className="font-medium">{(trend.engagementRate * 100).toFixed(1)}%</span>
                  </div>
                </div>
                
                <div className="mt-3">
                  <div className="text-xs text-gray-600 mb-1">트렌딩 코인:</div>
                  <div className="flex flex-wrap gap-1">
                    {trend.trendingCoins.map((coin, coinIndex) => (
                      <span key={coinIndex} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                        {coin}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="mt-3">
                  <div className="text-xs text-gray-600 mb-1">활성 시간:</div>
                  <div className="flex flex-wrap gap-1">
                    {trend.peakHours.map((hour, hourIndex) => (
                      <span key={hourIndex} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                        {hour}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 바이럴 콘텐츠 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="h-5 w-5 mr-2" />
            바이럴 콘텐츠 TOP 3
          </CardTitle>
          <CardDescription>가장 많은 참여를 얻은 암호화폐 관련 콘텐츠</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {viralContent.map((content, index) => (
              <div key={content.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-bold text-yellow-600">#{index + 1}</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{content.platform}</h4>
                      <p className="text-sm text-gray-500">{content.coinName} ({content.coinSymbol})</p>
                    </div>
                  </div>
                  <div className={`text-sm font-medium ${getViralityColor(content.viralityScore)}`}>
                    바이럴: {content.viralityScore}점
                  </div>
                </div>
                
                <p className="text-sm text-gray-700 mb-3 italic">"{content.content}"</p>
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center space-x-4">
                    <span className="flex items-center">
                      <Target className="h-3 w-3 mr-1" />
                      참여: {content.engagement.toLocaleString()}
                    </span>
                  </div>
                  <span>{new Date(content.timestamp).toLocaleString('ko-KR')}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
