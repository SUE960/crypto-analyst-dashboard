import { NextRequest, NextResponse } from 'next/server'
import { createDatabaseSchema, createIndexes, setupRLSPolicies } from '@/lib/supabase-setup'

export async function POST(request: NextRequest) {
  try {
    console.log('Supabase 데이터베이스 설정 시작...')

    // 데이터베이스 스키마 생성
    const schemaResult = await createDatabaseSchema()
    if (!schemaResult.success) {
      return NextResponse.json(
        { error: '데이터베이스 스키마 생성 실패', details: schemaResult.error },
        { status: 500 }
      )
    }

    // 인덱스 생성
    const indexResult = await createIndexes()
    if (!indexResult.success) {
      return NextResponse.json(
        { error: '인덱스 생성 실패', details: indexResult.error },
        { status: 500 }
      )
    }

    // RLS 정책 설정
    const policyResult = await setupRLSPolicies()
    if (!policyResult.success) {
      return NextResponse.json(
        { error: 'RLS 정책 설정 실패', details: policyResult.error },
        { status: 500 }
      )
    }

    return NextResponse.json({
      message: 'Supabase 데이터베이스 설정이 완료되었습니다!',
      success: true,
      results: {
        schema: schemaResult.success,
        indexes: indexResult.success,
        policies: policyResult.success
      }
    })

  } catch (error) {
    console.error('Supabase 설정 API 에러:', error)
    return NextResponse.json(
      { error: '서버 오류가 발생했습니다.', success: false },
      { status: 500 }
    )
  }
}
