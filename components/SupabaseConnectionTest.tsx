'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle, XCircle, Loader2, Database, Key, Settings } from 'lucide-react'

export default function SupabaseConnectionTest() {
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle')
  const [setupStatus, setSetupStatus] = useState<'idle' | 'setting' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState('')

  const testConnection = async () => {
    setConnectionStatus('testing')
    setErrorMessage('')

    try {
      const response = await fetch('/api/coin/BTC')
      if (response.ok) {
        setConnectionStatus('success')
      } else {
        setConnectionStatus('error')
        setErrorMessage('API 연결 실패')
      }
    } catch (error) {
      setConnectionStatus('error')
      setErrorMessage('연결 테스트 실패')
    }
  }

  const setupDatabase = async () => {
    setSetupStatus('setting')
    setErrorMessage('')

    try {
      const response = await fetch('/api/supabase-setup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const result = await response.json()
      
      if (response.ok && result.success) {
        setSetupStatus('success')
      } else {
        setSetupStatus('error')
        setErrorMessage(result.error || '데이터베이스 설정 실패')
      }
    } catch (error) {
      setSetupStatus('error')
      setErrorMessage('데이터베이스 설정 중 오류 발생')
    }
  }

  const createSampleData = async () => {
    try {
      const response = await fetch('/api/seed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      const result = await response.json()
      
      if (response.ok && result.success) {
        alert('샘플 데이터가 성공적으로 생성되었습니다!')
      } else {
        alert('샘플 데이터 생성 실패: ' + result.error)
      }
    } catch (error) {
      alert('샘플 데이터 생성 중 오류 발생')
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Database className="h-5 w-5 mr-2" />
            Supabase 연결 설정
          </CardTitle>
          <CardDescription>
            Supabase 데이터베이스 연결 및 설정을 확인하고 구성합니다.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 연결 테스트 */}
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center space-x-3">
              <Key className="h-4 w-4 text-muted-foreground" />
              <div>
                <div className="font-medium">데이터베이스 연결 테스트</div>
                <div className="text-sm text-muted-foreground">
                  Supabase API 연결 상태를 확인합니다
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {connectionStatus === 'testing' && <Loader2 className="h-4 w-4 animate-spin" />}
              {connectionStatus === 'success' && <CheckCircle className="h-4 w-4 text-green-500" />}
              {connectionStatus === 'error' && <XCircle className="h-4 w-4 text-red-500" />}
              <Button 
                onClick={testConnection} 
                disabled={connectionStatus === 'testing'}
                variant="outline"
                size="sm"
              >
                연결 테스트
              </Button>
            </div>
          </div>

          {/* 데이터베이스 설정 */}
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center space-x-3">
              <Settings className="h-4 w-4 text-muted-foreground" />
              <div>
                <div className="font-medium">데이터베이스 스키마 설정</div>
                <div className="text-sm text-muted-foreground">
                  테이블, 인덱스, RLS 정책을 생성합니다
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {setupStatus === 'setting' && <Loader2 className="h-4 w-4 animate-spin" />}
              {setupStatus === 'success' && <CheckCircle className="h-4 w-4 text-green-500" />}
              {setupStatus === 'error' && <XCircle className="h-4 w-4 text-red-500" />}
              <Button 
                onClick={setupDatabase} 
                disabled={setupStatus === 'setting'}
                variant="outline"
                size="sm"
              >
                스키마 설정
              </Button>
            </div>
          </div>

          {/* 샘플 데이터 생성 */}
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center space-x-3">
              <Database className="h-4 w-4 text-muted-foreground" />
              <div>
                <div className="font-medium">샘플 데이터 생성</div>
                <div className="text-sm text-muted-foreground">
                  테스트용 코인 데이터와 분석 정보를 생성합니다
                </div>
              </div>
            </div>
            <Button 
              onClick={createSampleData}
              variant="outline"
              size="sm"
            >
              샘플 데이터 생성
            </Button>
          </div>

          {/* 에러 메시지 */}
          {errorMessage && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
              <div className="flex items-center space-x-2">
                <XCircle className="h-4 w-4 text-red-500" />
                <span className="text-sm text-red-500">{errorMessage}</span>
              </div>
            </div>
          )}

          {/* 성공 메시지 */}
          {connectionStatus === 'success' && setupStatus === 'success' && (
            <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm text-green-500">
                  Supabase 연결 및 설정이 완료되었습니다!
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 설정 가이드 */}
      <Card>
        <CardHeader>
          <CardTitle>Supabase 설정 가이드</CardTitle>
          <CardDescription>
            다음 단계를 따라 Supabase를 완전히 설정하세요.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <h4 className="font-medium">1. Supabase 대시보드 접속</h4>
            <p className="text-sm text-muted-foreground">
              <a 
                href="https://supabase.com/dashboard" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                https://supabase.com/dashboard
              </a>에서 프로젝트에 접속하세요.
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">2. API 키 확인</h4>
            <p className="text-sm text-muted-foreground">
              Project Settings → API에서 anon public key를 복사하세요.
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">3. 환경 변수 설정</h4>
            <p className="text-sm text-muted-foreground">
              .env.local 파일에 NEXT_PUBLIC_SUPABASE_ANON_KEY를 설정하세요.
            </p>
            <code className="block p-2 bg-muted rounded text-xs">
              NEXT_PUBLIC_SUPABASE_ANON_KEY=your_actual_anon_key_here
            </code>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">4. 데이터베이스 설정</h4>
            <p className="text-sm text-muted-foreground">
              위의 "스키마 설정" 버튼을 클릭하여 테이블을 생성하세요.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
