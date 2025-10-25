'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, TrendingDown, Users, MessageSquare, Star, AlertTriangle } from 'lucide-react'

interface InfluencerMention {
  id: string
  influencerName: string
  platform: string
  coinSymbol: string
  coinName: string
  mentionType: 'positive' | 'negative' | 'neutral'
  sentimentScore: number
  reach: number
  engagement: number
  timestamp: string
  content: string
}

export default function InfluencerAnalysis() {
  const [mentions, setMentions] = useState<InfluencerMention[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchInfluencerMentions()
  }, [])

  const fetchInfluencerMentions = async () => {
    try {
      // 실제 API 호출 대신 샘플 데이터 사용
      const sampleData: InfluencerMention[] = [
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
      
      setMentions(sampleData)
    } catch (error) {
      console.error('인플루언서 언급 데이터 로딩 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return 'text-green-600'
    if (score < -0.3) return 'text-red-600'
    return 'text-gray-600'
  }

  const getSentimentIcon = (score: number) => {
    if (score > 0.3) return <TrendingUp className="h-4 w-4" />
    if (score < -0.3) return <TrendingDown className="h-4 w-4" />
    return <AlertTriangle className="h-4 w-4" />
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Star className="h-5 w-5 mr-2" />
            인플루언서 언급 분석
          </CardTitle>
          <CardDescription>주요 인플루언서들의 암호화폐 언급 현황</CardDescription>
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
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Star className="h-5 w-5 mr-2" />
          인플루언서 언급 분석
        </CardTitle>
        <CardDescription>주요 인플루언서들의 암호화폐 언급 현황</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {mentions.map((mention) => (
            <div key={mention.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Users className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{mention.influencerName}</h4>
                    <p className="text-sm text-gray-500">{mention.platform}</p>
                  </div>
                </div>
                <div className={`flex items-center space-x-1 ${getSentimentColor(mention.sentimentScore)}`}>
                  {getSentimentIcon(mention.sentimentScore)}
                  <span className="text-sm font-medium">
                    {(mention.sentimentScore * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              
              <div className="mb-2">
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2">
                  {mention.coinSymbol}
                </span>
                <span className="text-sm text-gray-600">{mention.coinName}</span>
              </div>
              
              <p className="text-sm text-gray-700 mb-3">{mention.content}</p>
              
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center space-x-4">
                  <span className="flex items-center">
                    <MessageSquare className="h-3 w-3 mr-1" />
                    도달: {mention.reach.toLocaleString()}
                  </span>
                  <span className="flex items-center">
                    <TrendingUp className="h-3 w-3 mr-1" />
                    참여: {mention.engagement.toLocaleString()}
                  </span>
                </div>
                <span>{new Date(mention.timestamp).toLocaleString('ko-KR')}</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
