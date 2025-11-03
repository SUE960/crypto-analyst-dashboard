'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { supabase, CoinData } from '@/lib/supabase'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function PriceChart() {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPriceData()
  }, [])

  const fetchPriceData = async () => {
    try {
      const { data: coins, error } = await supabase
        .from('coin_data')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(100)

      if (error) throw error

      // 시간별로 그룹화하여 차트 데이터 생성
      const chartData = coins?.reduce((acc: any, coin: CoinData) => {
        const date = new Date(coin.created_at).toLocaleDateString()
        const existing = acc.find((item: any) => item.date === date)
        
        if (existing) {
          existing[coin.symbol] = coin.current_price
        } else {
          acc.push({
            date,
            [coin.symbol]: coin.current_price
          })
        }
        
        return acc
      }, []) || []

      setData(chartData.slice(0, 30)) // 최근 30일 데이터만 표시
    } catch (error) {
      console.error('가격 데이터 로딩 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00']

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="date" 
            stroke="#9ca3af"
            fontSize={12}
          />
          <YAxis 
            stroke="#9ca3af"
            fontSize={12}
            tickFormatter={(value) => `$${value.toLocaleString()}`}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#f9fafb'
            }}
            formatter={(value: any) => [`$${value.toLocaleString()}`, '가격']}
          />
          {data.length > 0 && Object.keys(data[0]).filter(key => key !== 'date').slice(0, 5).map((symbol, index) => (
            <Line
              key={symbol}
              type="monotone"
              dataKey={symbol}
              stroke={colors[index % colors.length]}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
