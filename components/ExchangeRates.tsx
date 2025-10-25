'use client'

import { TrendingUp, TrendingDown } from 'lucide-react'

interface ExchangeRateProps {
  country: string
  pair: string
  rate: number
  change: number
  changePercent: number
}

export default function ExchangeRate({ country, pair, rate, change, changePercent }: ExchangeRateProps) {
  const isUp = change >= 0
  const changeColor = isUp ? 'text-red-500' : 'text-blue-500'
  const changeIcon = isUp ? TrendingUp : TrendingDown

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-3 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <span className="text-sm font-medium text-gray-600">{country}</span>
          <span className="text-xs text-gray-500">{pair}</span>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-sm font-bold text-gray-900">{rate.toLocaleString()}</span>
          <div className={`flex items-center text-xs ${changeColor}`}>
            {isUp ? (
              <TrendingUp className="h-3 w-3 mr-1" />
            ) : (
              <TrendingDown className="h-3 w-3 mr-1" />
            )}
            <span>{change.toFixed(2)} ({changePercent.toFixed(2)}%)</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ExchangeRatesSection() {
  const exchangeRates = [
    {
      country: '미국',
      pair: 'USD/KRW',
      rate: 1439.80,
      change: 2.30,
      changePercent: 0.16
    },
    {
      country: '일본',
      pair: 'JPY/KRW',
      rate: 941.75,
      change: -0.35,
      changePercent: -0.04
    },
    {
      country: '중국',
      pair: 'CNY/KRW',
      rate: 202.10,
      change: 0.33,
      changePercent: 0.16
    },
    {
      country: '유로',
      pair: 'EUR/KRW',
      rate: 1674.13,
      change: 3.90,
      changePercent: 0.23
    }
  ]

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">오늘의 환율</h3>
      <div className="grid grid-cols-2 gap-3">
        {exchangeRates.map((rate, index) => (
          <ExchangeRate
            key={index}
            country={rate.country}
            pair={rate.pair}
            rate={rate.rate}
            change={rate.change}
            changePercent={rate.changePercent}
          />
        ))}
      </div>
    </div>
  )
}
