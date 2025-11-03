'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { TrendingUp, TrendingDown, Star } from 'lucide-react'

interface Coin {
  symbol: string
  name: string
  price: number
  change24h: number
  changePercent24h: number
  marketCap: number
  volume: number
  logo: string
}

interface CoinBannerProps {
  selectedCoin: string
  onCoinSelect: (symbol: string) => void
}

export default function CoinBanner({ selectedCoin, onCoinSelect }: CoinBannerProps) {
  const [coins] = useState<Coin[]>([
    {
      symbol: 'BTC',
      name: 'Bitcoin',
      price: 43250.50,
      change24h: 1250.30,
      changePercent24h: 2.98,
      marketCap: 850000000000,
      volume: 25000000000,
      logo: '₿'
    },
    {
      symbol: 'ETH',
      name: 'Ethereum',
      price: 2650.75,
      change24h: -45.20,
      changePercent24h: -1.68,
      marketCap: 320000000000,
      volume: 15000000000,
      logo: 'Ξ'
    },
    {
      symbol: 'BNB',
      name: 'Binance Coin',
      price: 315.80,
      change24h: 8.45,
      changePercent24h: 2.75,
      marketCap: 48000000000,
      volume: 1200000000,
      logo: '🟡'
    },
    {
      symbol: 'SOL',
      name: 'Solana',
      price: 98.25,
      change24h: -2.15,
      changePercent24h: -2.14,
      marketCap: 42000000000,
      volume: 2800000000,
      logo: '◎'
    },
    {
      symbol: 'ADA',
      name: 'Cardano',
      price: 0.485,
      change24h: 0.012,
      changePercent24h: 2.54,
      marketCap: 17000000000,
      volume: 450000000,
      logo: '₳'
    },
    {
      symbol: 'DOGE',
      name: 'Dogecoin',
      price: 0.0825,
      change24h: 0.0035,
      changePercent24h: 4.44,
      marketCap: 12000000000,
      volume: 850000000,
      logo: '🐕'
    },
    {
      symbol: 'MATIC',
      name: 'Polygon',
      price: 0.875,
      change24h: -0.025,
      changePercent24h: -2.78,
      marketCap: 8500000000,
      volume: 320000000,
      logo: '⬟'
    },
    {
      symbol: 'AVAX',
      name: 'Avalanche',
      price: 35.20,
      change24h: 1.15,
      changePercent24h: 3.38,
      marketCap: 13000000000,
      volume: 680000000,
      logo: '🔺'
    }
  ])

  const formatPrice = (price: number) => {
    if (price < 1) {
      return price.toFixed(4)
    } else if (price < 100) {
      return price.toFixed(2)
    } else {
      return price.toLocaleString('ko-KR', { maximumFractionDigits: 2 })
    }
  }

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e12) {
      return `$${(marketCap / 1e12).toFixed(1)}T`
    } else if (marketCap >= 1e9) {
      return `$${(marketCap / 1e9).toFixed(1)}B`
    } else if (marketCap >= 1e6) {
      return `$${(marketCap / 1e6).toFixed(1)}M`
    } else {
      return `$${marketCap.toLocaleString()}`
    }
  }

  const getChangeColor = (change: number) => {
    return change >= 0 ? 'text-red-500' : 'text-blue-500'
  }

  const getChangeIcon = (change: number) => {
    return change >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />
  }

  return (
    <Card className="mb-6">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">코인 선택</h3>
          <div className="flex items-center text-sm text-gray-500">
            <Star className="h-4 w-4 mr-1" />
            현재 선택: {selectedCoin}
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
          {coins.map((coin) => (
            <button
              key={coin.symbol}
              onClick={() => onCoinSelect(coin.symbol)}
              className={`p-3 rounded-lg border-2 transition-all duration-200 hover:shadow-md ${
                selectedCoin === coin.symbol
                  ? 'border-blue-500 bg-blue-50 shadow-md'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="text-center">
                {/* 코인 로고 */}
                <div className="text-2xl mb-2">{coin.logo}</div>
                
                {/* 코인 심볼과 이름 */}
                <div className="font-medium text-gray-900 text-sm">{coin.symbol}</div>
                <div className="text-xs text-gray-500 truncate">{coin.name}</div>
                
                {/* 현재 가격 */}
                <div className="text-sm font-bold text-gray-900 mt-1">
                  ${formatPrice(coin.price)}
                </div>
                
                {/* 24시간 변동률 */}
                <div className={`flex items-center justify-center text-xs mt-1 ${getChangeColor(coin.change24h)}`}>
                  {getChangeIcon(coin.change24h)}
                  <span className="ml-1">{coin.changePercent24h.toFixed(2)}%</span>
                </div>
                
                {/* 시가총액 */}
                <div className="text-xs text-gray-500 mt-1">
                  {formatMarketCap(coin.marketCap)}
                </div>
              </div>
            </button>
          ))}
        </div>
        
        {/* 선택된 코인 상세 정보 */}
        {selectedCoin && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            {(() => {
              const coin = coins.find(c => c.symbol === selectedCoin)
              if (!coin) return null
              
              return (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">현재 가격:</span>
                    <div className="font-bold text-gray-900">${formatPrice(coin.price)}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">24시간 변동:</span>
                    <div className={`font-bold ${getChangeColor(coin.change24h)}`}>
                      ${formatPrice(Math.abs(coin.change24h))} ({coin.changePercent24h.toFixed(2)}%)
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-600">시가총액:</span>
                    <div className="font-bold text-gray-900">{formatMarketCap(coin.marketCap)}</div>
                  </div>
                  <div>
                    <span className="text-gray-600">24시간 거래량:</span>
                    <div className="font-bold text-gray-900">{formatMarketCap(coin.volume)}</div>
                  </div>
                </div>
              )
            })()}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
