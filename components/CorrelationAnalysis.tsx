'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter } from 'recharts'
import { supabase, CorrelationAnalysis } from '@/lib/supabase'
import { TrendingUp, Target, MessageSquare } from 'lucide-react'

export default function CorrelationAnalysisComponent() {
  const [correlations, setCorrelations] = useState<CorrelationAnalysis[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCorrelationData()
  }, [])

  const fetchCorrelationData = async () => {
    try {
      const { data, error } = await supabase
        .from('correlation_analysis')
        .select('*')
        .order('analysis_date', { ascending: false })
        .limit(50)

      if (error) throw error
      setCorrelations(data || [])
    } catch (error) {
      console.error('상관성 분석 데이터 로딩 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCorrelationStrength = (value: number) => {
    const abs = Math.abs(value)
    if (abs >= 0.7) return { strength: '강함', color: 'text-green-500' }
    if (abs >= 0.3) return { strength: '보통', color: 'text-yellow-500' }
    return { strength: '약함', color: 'text-red-500' }
  }

  const getCorrelationDirection = (value: number) => {
    return value > 0 ? '양의 상관관계' : '음의 상관관계'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  // 차트 데이터 준비
  const chartData = correlations.map(corr => ({
    coin: corr.coin_symbol,
    analyst: corr.analyst_correlation || 0,
    sentiment: corr.sentiment_correlation || 0,
    price: corr.price_correlation || 0
  }))

  return (
    <div className="space-y-6">
      {/* 상관성 요약 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <Target className="h-4 w-4 mr-2" />
              애널리스트 상관성
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {correlations.length > 0 ? 
                (correlations.reduce((sum, c) => sum + (c.analyst_correlation || 0), 0) / correlations.length).toFixed(3) : 
                '0.000'
              }
            </div>
            <p className="text-xs text-muted-foreground">
              목표가 정확도
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <MessageSquare className="h-4 w-4 mr-2" />
              감정 상관성
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {correlations.length > 0 ? 
                (correlations.reduce((sum, c) => sum + (c.sentiment_correlation || 0), 0) / correlations.length).toFixed(3) : 
                '0.000'
              }
            </div>
            <p className="text-xs text-muted-foreground">
              트윗 감정 영향도
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <TrendingUp className="h-4 w-4 mr-2" />
              가격 상관성
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {correlations.length > 0 ? 
                (correlations.reduce((sum, c) => sum + (c.price_correlation || 0), 0) / correlations.length).toFixed(3) : 
                '0.000'
              }
            </div>
            <p className="text-xs text-muted-foreground">
              시장 반응도
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 상관성 차트 */}
      <Card>
        <CardHeader>
          <CardTitle>상관성 분석 차트</CardTitle>
          <CardDescription>코인별 애널리스트, 감정, 가격 상관성 비교</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="coin" 
                  stroke="#9ca3af"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#9ca3af"
                  fontSize={12}
                  domain={[-1, 1]}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f9fafb'
                  }}
                />
                <Bar dataKey="analyst" fill="#8884d8" name="애널리스트" />
                <Bar dataKey="sentiment" fill="#82ca9d" name="감정" />
                <Bar dataKey="price" fill="#ffc658" name="가격" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* 상세 상관성 분석 */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">상세 상관성 분석</h3>
        {correlations.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            상관성 분석 데이터가 없습니다.
          </div>
        ) : (
          correlations.map((corr) => (
            <Card key={corr.id} className="hover:bg-accent/50 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="font-semibold text-lg">{corr.coin_symbol}</span>
                    <span className="text-sm text-muted-foreground">
                      {new Date(corr.analysis_date).toLocaleDateString('ko-KR')}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* 애널리스트 상관성 */}
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Target className="h-4 w-4 text-primary" />
                      <span className="text-sm font-medium">애널리스트</span>
                    </div>
                    <div className="text-lg font-semibold">
                      {(corr.analyst_correlation || 0).toFixed(3)}
                    </div>
                    <div className={`text-xs ${getCorrelationStrength(corr.analyst_correlation || 0).color}`}>
                      {getCorrelationStrength(corr.analyst_correlation || 0).strength} · {getCorrelationDirection(corr.analyst_correlation || 0)}
                    </div>
                  </div>

                  {/* 감정 상관성 */}
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <MessageSquare className="h-4 w-4 text-primary" />
                      <span className="text-sm font-medium">감정</span>
                    </div>
                    <div className="text-lg font-semibold">
                      {(corr.sentiment_correlation || 0).toFixed(3)}
                    </div>
                    <div className={`text-xs ${getCorrelationStrength(corr.sentiment_correlation || 0).color}`}>
                      {getCorrelationStrength(corr.sentiment_correlation || 0).strength} · {getCorrelationDirection(corr.sentiment_correlation || 0)}
                    </div>
                  </div>

                  {/* 가격 상관성 */}
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-primary" />
                      <span className="text-sm font-medium">가격</span>
                    </div>
                    <div className="text-lg font-semibold">
                      {(corr.price_correlation || 0).toFixed(3)}
                    </div>
                    <div className={`text-xs ${getCorrelationStrength(corr.price_correlation || 0).color}`}>
                      {getCorrelationStrength(corr.price_correlation || 0).strength} · {getCorrelationDirection(corr.price_correlation || 0)}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
