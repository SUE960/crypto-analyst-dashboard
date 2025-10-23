'use client'

import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { TrendingUp, TrendingDown, Target, MessageSquare, BarChart3, Users } from 'lucide-react'
import PriceChart from '@/components/PriceChart'
import AnalystTargets from '@/components/AnalystTargets'
import SentimentAnalysis from '@/components/SentimentAnalysis'
import CorrelationAnalysis from '@/components/CorrelationAnalysis'
import SupabaseConnectionTest from '@/components/SupabaseConnectionTest'

export default function Home() {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalCoins: 0,
    totalAnalysts: 0,
    totalTweets: 0,
    avgCorrelation: 0
  })

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      // 통계 데이터 가져오기
      const [coinsResult, analystsResult, tweetsResult, correlationResult] = await Promise.all([
        supabase.from('coin_data').select('*', { count: 'exact', head: true }),
        supabase.from('analyst_targets').select('*', { count: 'exact', head: true }),
        supabase.from('tweet_sentiments').select('*', { count: 'exact', head: true }),
        supabase.from('correlation_analysis').select('analyst_correlation')
      ])

      setStats({
        totalCoins: coinsResult.count || 0,
        totalAnalysts: analystsResult.count || 0,
        totalTweets: tweetsResult.count || 0,
        avgCorrelation: correlationResult.data?.length ? 
          correlationResult.data.reduce((sum, item) => sum + (item.analyst_correlation || 0), 0) / correlationResult.data.length : 0
      })
    } catch (error) {
      console.error('통계 데이터 로딩 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          Crypto Analyst Dashboard
        </h1>
        <p className="text-muted-foreground text-lg">
          애널리스트 목표가와 소셜 미디어 감정 분석을 통한 암호화폐 투자 인사이트
        </p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">추적 코인 수</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalCoins}</div>
            <p className="text-xs text-muted-foreground">
              실시간 모니터링 중
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">애널리스트 수</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalAnalysts}</div>
            <p className="text-xs text-muted-foreground">
              전문가 의견 수집
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">분석된 트윗</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalTweets}</div>
            <p className="text-xs text-muted-foreground">
              감정 분석 완료
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">평균 상관성</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.avgCorrelation > 0 ? (
                <span className="text-green-500 flex items-center">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  {(stats.avgCorrelation * 100).toFixed(1)}%
                </span>
              ) : (
                <span className="text-red-500 flex items-center">
                  <TrendingDown className="h-4 w-4 mr-1" />
                  {(stats.avgCorrelation * 100).toFixed(1)}%
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              목표가 정확도
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 메인 콘텐츠 */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">개요</TabsTrigger>
          <TabsTrigger value="analysts">애널리스트</TabsTrigger>
          <TabsTrigger value="sentiment">감정 분석</TabsTrigger>
          <TabsTrigger value="correlation">상관성 분석</TabsTrigger>
          <TabsTrigger value="setup">Supabase 설정</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>가격 추이</CardTitle>
                <CardDescription>주요 코인의 가격 변화 추이</CardDescription>
              </CardHeader>
              <CardContent>
                <PriceChart />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>애널리스트 목표가</CardTitle>
                <CardDescription>전문가들의 목표가 예측</CardDescription>
              </CardHeader>
              <CardContent>
                <AnalystTargets />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analysts">
          <AnalystTargets />
        </TabsContent>

        <TabsContent value="sentiment">
          <SentimentAnalysis />
        </TabsContent>

        <TabsContent value="correlation">
          <CorrelationAnalysis />
        </TabsContent>

        <TabsContent value="setup">
          <SupabaseConnectionTest />
        </TabsContent>
      </Tabs>
    </div>
  )
}
