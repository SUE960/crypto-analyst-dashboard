'use client'

import { useState } from 'react'
import { ChevronDown, Headphones, Globe, Menu, X } from 'lucide-react'

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="bg-[#1e3a8a] text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* 로고 */}
          <div className="flex items-center">
            <div className="text-2xl font-bold text-white">
              CryptoAnalyst
            </div>
          </div>

          {/* 데스크톱 네비게이션 */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-white hover:text-blue-200 transition-colors">
              거래소
            </a>
            <a href="#" className="text-white hover:text-blue-200 transition-colors">
              입출금
            </a>
            <a href="#" className="text-white hover:text-blue-200 transition-colors">
              투자내역
            </a>
            <a href="#" className="text-white hover:text-blue-200 transition-colors">
              코인동향
            </a>
            <div className="relative group">
              <button className="text-white hover:text-blue-200 transition-colors flex items-center">
                서비스 더보기
                <ChevronDown className="ml-1 h-4 w-4" />
              </button>
            </div>
            <div className="relative group">
              <button className="text-white hover:text-blue-200 transition-colors flex items-center">
                투자 리그
                <ChevronDown className="ml-1 h-4 w-4" />
              </button>
            </div>
          </nav>

          {/* 우측 버튼들 */}
          <div className="flex items-center space-x-4">
            <button className="text-white hover:text-blue-200 transition-colors">
              로그인
            </button>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors">
              회원가입
            </button>
            <button className="text-white hover:text-blue-200 transition-colors">
              <Headphones className="h-5 w-5" />
            </button>
            <button className="text-white hover:text-blue-200 transition-colors">
              <Globe className="h-5 w-5" />
            </button>
            
            {/* 모바일 메뉴 버튼 */}
            <button
              className="md:hidden text-white hover:text-blue-200 transition-colors"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* 모바일 메뉴 */}
        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-[#1e3a8a]">
              <a href="#" className="text-white block px-3 py-2 hover:text-blue-200">
                거래소
              </a>
              <a href="#" className="text-white block px-3 py-2 hover:text-blue-200">
                입출금
              </a>
              <a href="#" className="text-white block px-3 py-2 hover:text-blue-200">
                투자내역
              </a>
              <a href="#" className="text-white block px-3 py-2 hover:text-blue-200">
                코인동향
              </a>
              <a href="#" className="text-white block px-3 py-2 hover:text-blue-200">
                서비스 더보기
              </a>
              <a href="#" className="text-white block px-3 py-2 hover:text-blue-200">
                투자 리그
              </a>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
