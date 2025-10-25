'use client'

import { ChevronLeft, ChevronRight } from 'lucide-react'

interface NewsItemProps {
  title: string
  time: string
}

function NewsItem({ title, time }: NewsItemProps) {
  return (
    <div className="py-2 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 rounded px-2">
      <p className="text-sm text-gray-900 mb-1">{title}</p>
      <span className="text-xs text-gray-500">{time}</span>
    </div>
  )
}

export default function NewsSection() {
  const newsItems = [
    {
      title: "[1보]뉴욕증시, 금리인하 뒷받침 하는 소비자물가에 강세 마감",
      time: "05:35"
    },
    {
      title: "미구 \"트럼프 인버스바서 기저 마나 이전 어기마 별도 가능\" 11브전",
      time: "11:00"
    },
    {
      title: "비토크의 해권의에 떠어진까? 신의 대답은 'YES' 16년전",
      time: "16:00"
    }
  ]

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* 시황 헤더 */}
      <div className="bg-[#1e3a8a] text-white px-4 py-3 rounded-t-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">10.25 (토) 시황</span>
          <div className="flex items-center space-x-2">
            <button className="text-white hover:text-blue-200">
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button className="text-white hover:text-blue-200">
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* 메인 뉴스 */}
      <div className="p-4 border-b border-gray-200">
        <p className="text-sm text-gray-900 font-medium">
          [1보]뉴욕증시, 금리인하 뒷받침 하는 소비자물가에 강세 마감 05:35
        </p>
      </div>

      {/* 뉴스 리스트 */}
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">최신 뉴스</h3>
          <div className="flex items-center space-x-2">
            <button className="text-gray-400 hover:text-gray-600">
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="text-xs text-gray-500">1/5</span>
            <button className="text-gray-400 hover:text-gray-600">
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
        <div className="space-y-1">
          {newsItems.map((news, index) => (
            <NewsItem
              key={index}
              title={news.title}
              time={news.time}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
