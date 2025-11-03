'use client'

interface WeeklyGainerProps {
  rank: number
  name: string
  ticker: string
  pair: string
  gainPercent: number
}

function WeeklyGainer({ rank, name, ticker, pair, gainPercent }: WeeklyGainerProps) {
  return (
    <div className="flex items-center justify-between py-2 hover:bg-gray-50 rounded px-2">
      <div className="flex items-center space-x-3">
        <span className="text-sm font-medium text-gray-600 w-6">{rank}</span>
        <div className="flex flex-col">
          <span className="text-sm font-medium text-gray-900">{name}</span>
          <span className="text-xs text-gray-500">{ticker}/{pair}</span>
        </div>
      </div>
      <span className="text-sm font-bold text-red-500">+{gainPercent.toFixed(2)}%</span>
    </div>
  )
}

export default function WeeklyGainersSection() {
  const weeklyGainers = [
    { rank: 1, name: '신퓨처스', ticker: 'F', pair: 'KRW', gainPercent: 225.00 },
    { rank: 2, name: '아반티스', ticker: 'AVNT', pair: 'KRW', gainPercent: 58.86 },
    { rank: 3, name: '아이오에스티', ticker: 'IOST', pair: 'BTC', gainPercent: 50.00 },
    { rank: 4, name: '바이오프로토콜', ticker: 'BIO', pair: 'BTC', gainPercent: 37.93 },
    { rank: 5, name: '오션프로토콜', ticker: 'OCEAN', pair: 'BTC', gainPercent: 37.80 },
    { rank: 6, name: '팔콘파이낸스', ticker: 'FF', pair: 'KRW', gainPercent: 36.02 },
    { rank: 7, name: '소폰', ticker: 'SOPH', pair: 'KRW', gainPercent: 35.12 },
    { rank: 8, name: '오덜리', ticker: 'ORDER', pair: 'BTC', gainPercent: 33.66 },
    { rank: 9, name: '너보스', ticker: 'CKB', pair: 'BTC', gainPercent: 33.33 },
    { rank: 10, name: '미라네트워크', ticker: 'MIRA', pair: 'BTC', gainPercent: 32.32 }
  ]

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">주간 상승률</h3>
        <span className="text-xs text-gray-500">10.25 09:30 기준</span>
      </div>
      <div className="space-y-1">
        {weeklyGainers.map((gainer) => (
          <WeeklyGainer
            key={gainer.rank}
            rank={gainer.rank}
            name={gainer.name}
            ticker={gainer.ticker}
            pair={gainer.pair}
            gainPercent={gainer.gainPercent}
          />
        ))}
      </div>
    </div>
  )
}
