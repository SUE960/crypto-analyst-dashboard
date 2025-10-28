#!/usr/bin/env python3
"""
Supabase 연결 테스트 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from config import Config

def test_supabase_connection():
    """Supabase 연결 테스트"""
    print("🔍 Supabase 연결 테스트 시작...")
    
    # 설정 확인
    print(f"URL: {Config.SUPABASE_URL}")
    print(f"Service Key: {Config.SUPABASE_SERVICE_ROLE_KEY[:20]}..." if Config.SUPABASE_SERVICE_ROLE_KEY else "None")
    
    if not Config.SUPABASE_URL or not Config.SUPABASE_SERVICE_ROLE_KEY:
        print("❌ Supabase 설정이 누락되었습니다")
        return False
    
    try:
        # 클라이언트 생성
        client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        print("✅ Supabase 클라이언트 생성 성공")
        
        # 테이블 존재 확인
        try:
            response = client.table('cryptocurrencies').select('count').execute()
            print("✅ cryptocurrencies 테이블 접근 성공")
            print(f"레코드 수: {response.data}")
            return True
        except Exception as e:
            print(f"❌ cryptocurrencies 테이블 접근 실패: {e}")
            
            # 다른 테이블 확인
            try:
                response = client.table('test_table').select('count').execute()
                print("✅ test_table 테이블 접근 성공")
                return True
            except Exception as e2:
                print(f"❌ test_table 테이블 접근 실패: {e2}")
                
                # 스키마 정보 확인
                try:
                    response = client.table('information_schema.tables').select('*').execute()
                    print("✅ 스키마 정보 조회 성공")
                    print("사용 가능한 테이블들:")
                    for table in response.data[:10]:  # 처음 10개만
                        print(f"  - {table.get('table_name', 'Unknown')}")
                    return True
                except Exception as e3:
                    print(f"❌ 스키마 정보 조회 실패: {e3}")
                    return False
        
    except Exception as e:
        print(f"❌ Supabase 클라이언트 생성 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    if success:
        print("\n🎉 연결 테스트 성공!")
    else:
        print("\n💥 연결 테스트 실패!")
        print("\n📋 해결 방법:")
        print("1. Supabase Dashboard에서 SQL Editor 열기")
        print("2. simple-schema.sql 파일 내용 실행")
        print("3. 다시 테스트 실행")
