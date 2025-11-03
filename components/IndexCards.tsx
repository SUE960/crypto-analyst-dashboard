'use client'

import { TrendingUp, TrendingDown } from 'lucide-react'

interface IndexCardProps {
  title: string
  value: number
  change: number
  changePercent: number
  isPositive?: boolean
}

export default function IndexCard({ title, value, change, changePercent, isPositive = true }: IndexCardProps) {
  const isUp = change >= 0
  const changeColor = isUp ? 'text-red-500' : 'text-blue-500'
  const changeIcon = isUp ? TrendingUp : TrendingDown

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex flex-col">
        <h3 className="text-sm font-medium text-gray-600 mb-2">{title}</h3>
        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-lg font-bold text-gray-900">
              {value.toLocaleString()}
            </span>
            <div className={`flex items-center text-sm ${changeColor}`}>
              {isUp ? (
                <TrendingUp className="h-3 w-3 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1" />
              )}
              <span>{change.toFixed(2)} ({changePercent.toFixed(2)}%)</span>
            </div>
          </div>
          <div className="w-16 h-8 bg-gray-100 rounded flex items-center justify-center">
            <div className="text-xs text-gray-500">차트</div>
          </div>
        </div>
      </div>
    </div>
  )
}

// 종합지수 카드들
export function CompositeIndexCard() {
  return (
    <IndexCard
      title="CryptoAnalyst 종합 지수"
      value={17212.68}
      change={-17.54}
      changePercent={-0.10}
      isPositive={false}
    />
  )
}

export function AltcoinIndexCard() {
  return (
    <IndexCard
      title="CryptoAnalyst 알트코인 지수"
      value={5547.93}
      change={-14.91}
      changePercent={-0.27}
      isPositive={false}
    />
  )
}

export function CryptoAnalyst10Card() {
  return (
    <IndexCard
      title="CryptoAnalyst 10"
      value={4610.75}
      change={-6.922}
      changePercent={-0.15}
      isPositive={false}
    />
  )
}

export function CryptoAnalyst30Card() {
  return (
    <IndexCard
      title="CryptoAnalyst 30"
      value={4127.68}
      change={-5.943}
      changePercent={-0.14}
      isPositive={false}
    />
  )
}

export function BitcoinGroupCard() {
  return (
    <IndexCard
      title="비트코인 그룹"
      value={29772.15}
      change={-14.48}
      changePercent={-0.05}
      isPositive={false}
    />
  )
}

export function EthereumGroupCard() {
  return (
    <IndexCard
      title="이더리움 그룹"
      value={16451.72}
      change={-53.27}
      changePercent={-0.32}
      isPositive={false}
    />
  )
}
