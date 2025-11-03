#!/usr/bin/env python3
"""
Dispersion Signal 실행 예시 스크립트
실제 환경에서 테스트하기 전에 사용할 수 있는 예시 코드
"""
import os
import sys
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from collectors.cryptoquant import CryptoQuantCollector
from database.supabase_client import SupabaseClient
from utils.logger import setup_logger

def test_cryptoquant_api():
    """CryptoQuant API 테스트"""
    print("🔍 CryptoQuant API 테스트 중...")
    
    try:
        # API 키 확인
        api_key = os.getenv('CRYPTOQUANT_API_KEY')
        if not api_key:
            print("❌ CRYPTOQUANT_API_KEY 환경변수가 설정되지 않았습니다")
            return False
        
        # 수집기 초기화
        collector = CryptoQuantCollector(api_key)
        
        # 테스트 데이터 수집 (최근 1일)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        print(f"📅 수집 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        
        # BTC 데이터 수집 테스트
        data = collector.collect_data('btc', start_date, end_date, '1hour')
        
        if data:
            print(f"✅ 데이터 수집 성공: {len(data)}개 레코드")
            print("📊 샘플 데이터:")
            for i, record in enumerate(data[:3]):
                print(f"  {i+1}. {record['timestamp']}: 넷플로우={record.get('exchange_netflow', 'N/A')}")
            return True
        else:
            print("❌ 데이터 수집 실패")
            return False
            
    except Exception as e:
        print(f"❌ API 테스트 실패: {e}")
        return False

def test_supabase_connection():
    """Supabase 연결 테스트"""
    print("\n🔍 Supabase 연결 테스트 중...")
    
    try:
        # Supabase 클라이언트 초기화
        client = SupabaseClient(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        
        # 연결 테스트
        if client.test_connection():
            print("✅ Supabase 연결 성공")
            
            # 코인 목록 조회 테스트
            crypto_list = client.get_crypto_list()
            print(f"📋 등록된 코인 수: {len(crypto_list)}")
            
            for crypto in crypto_list[:3]:
                print(f"  - {crypto['symbol']}: {crypto['name']}")
            
            return True
        else:
            print("❌ Supabase 연결 실패")
            return False
            
    except Exception as e:
        print(f"❌ Supabase 테스트 실패: {e}")
        return False

def test_data_flow():
    """전체 데이터 플로우 테스트"""
    print("\n🔍 전체 데이터 플로우 테스트 중...")
    
    try:
        # 로거 설정
        logger = setup_logger('test', 'logs/test.log', 'INFO')
        
        # 클라이언트 초기화
        supabase_client = SupabaseClient(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
        collector = CryptoQuantCollector(Config.CRYPTOQUANT_API_KEY)
        
        # BTC 코인 ID 조회
        crypto_id = supabase_client.get_crypto_id('BTC')
        if not crypto_id:
            print("❌ BTC 코인을 찾을 수 없습니다")
            return False
        
        print(f"📋 BTC 코인 ID: {crypto_id}")
        
        # 최근 1시간 데이터 수집
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=1)
        
        print(f"📅 수집 기간: {start_date.strftime('%Y-%m-%d %H:%M')} ~ {end_date.strftime('%Y-%m-%d %H:%M')}")
        
        # 데이터 수집
        raw_data = collector.collect_data('btc', start_date, end_date, '1hour')
        
        if not raw_data:
            print("❌ 데이터 수집 실패")
            return False
        
        print(f"✅ 데이터 수집 성공: {len(raw_data)}개 레코드")
        
        # 데이터 변환 (간단한 테스트)
        from database.models import OnchainMetric
        
        metrics = []
        for record in raw_data[:2]:  # 처음 2개만 테스트
            try:
                timestamp = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                
                metric = OnchainMetric(
                    crypto_id=crypto_id,
                    timestamp=timestamp,
                    exchange_netflow=record.get('exchange_netflow'),
                    exchange_reserve=record.get('exchange_reserve'),
                    active_addresses=record.get('active_addresses'),
                    data_source='cryptoquant',
                    raw_data=record.get('raw_data', {})
                )
                
                metrics.append(metric)
                print(f"  ✅ 데이터 변환 성공: {timestamp}")
                
            except Exception as e:
                print(f"  ❌ 데이터 변환 실패: {e}")
                continue
        
        if metrics:
            print(f"✅ 데이터 변환 성공: {len(metrics)}개 레코드")
            print("🎉 전체 데이터 플로우 테스트 완료!")
            return True
        else:
            print("❌ 데이터 변환 실패")
            return False
            
    except Exception as e:
        print(f"❌ 데이터 플로우 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 Dispersion Signal 테스트 시작")
    print("=" * 50)
    
    # 환경변수 로드
    from dotenv import load_dotenv
    load_dotenv()
    
    # 테스트 실행
    tests = [
        ("CryptoQuant API", test_cryptoquant_api),
        ("Supabase 연결", test_supabase_connection),
        ("데이터 플로우", test_data_flow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "="*50)
    print("📊 테스트 결과 요약")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\n총 {len(results)}개 테스트 중 {passed}개 통과")
    
    if passed == len(results):
        print("🎉 모든 테스트 통과! 시스템이 정상적으로 작동합니다.")
        return True
    else:
        print("⚠️  일부 테스트 실패. 설정을 확인해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
