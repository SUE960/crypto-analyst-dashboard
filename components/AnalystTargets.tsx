'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { supabase, AnalystTarget } from '@/lib/supabase'
import { TrendingUp, TrendingDown, Target, Users } from 'lucide-react'

export default function AnalystTargets() {
  const [targets, setTargets] = useState<AnalystTarget[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalystTargets()
  }, [])

  const fetchAnalystTargets = async () => {
    try {
      const { data, error } = await supabase
        .from('analyst_targets')
        .select('*')
        .order('analysis_date', { ascending: false })
        .limit(20)

      if (error) throw error
      setTargets(data || [])
    } catch (error) {
      console.error('애널리스트 목표가 로딩 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const calculateAccuracy = (target: AnalystTarget) => {
    const accuracy = ((target.target_price - target.current_price) / target.current_price) * 100
    return accuracy
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {targets.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          애널리스트 목표가 데이터가 없습니다.
        </div>
      ) : (
        targets.map((target) => {
          const accuracy = calculateAccuracy(target)
          const isPositive = accuracy > 0
          
          return (
            <Card key={target.id} className="hover:bg-accent/50 transition-colors">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2">
                      <Target className="h-4 w-4 text-primary" />
                      <span className="font-semibold">{target.coin_symbol}</span>
                    </div>
                    <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                      <Users className="h-3 w-3" />
                      <span>{target.analyst_name}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">현재가</div>
                      <div className="font-semibold">${target.current_price.toLocaleString()}</div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">목표가</div>
                      <div className="font-semibold">${target.target_price.toLocaleString()}</div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">예상 수익률</div>
                      <div className={`font-semibold flex items-center ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                        {isPositive ? (
                          <TrendingUp className="h-3 w-3 mr-1" />
                        ) : (
                          <TrendingDown className="h-3 w-3 mr-1" />
                        )}
                        {Math.abs(accuracy).toFixed(1)}%
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">신뢰도</div>
                      <div className="font-semibold">
                        {(target.confidence_score * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-3 text-xs text-muted-foreground">
                  분석일: {new Date(target.analysis_date).toLocaleDateString('ko-KR')}
                </div>
              </CardContent>
            </Card>
          )
        })
      )}
    </div>
  )
}
