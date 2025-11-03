import { NextRequest, NextResponse } from 'next/server'
import { seedDatabase } from '@/lib/seed'

export async function POST(request: NextRequest) {
  try {
    const result = await seedDatabase()
    
    if (result.success) {
      return NextResponse.json({ 
        message: '샘플 데이터가 성공적으로 생성되었습니다.',
        success: true 
      })
    } else {
      return NextResponse.json(
        { error: '샘플 데이터 생성 중 오류가 발생했습니다.', success: false },
        { status: 500 }
      )
    }
  } catch (error) {
    console.error('시딩 API 에러:', error)
    return NextResponse.json(
      { error: '서버 오류가 발생했습니다.', success: false },
      { status: 500 }
    )
  }
}
