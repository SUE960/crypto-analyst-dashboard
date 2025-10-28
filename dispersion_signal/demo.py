#!/usr/bin/env python3
"""
Dispersion Signal 데모 스크립트
실제 API 키 없이도 프로젝트 구조와 기능을 확인할 수 있습니다.
"""
import os
import sys
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_project_structure():
    """프로젝트 구조 데모"""
    print("🏗️  Dispersion Signal 프로젝트 구조")
    print("=" * 50)
    
    structure = """
dispersion_signal/
├── 📄 main.py                    # 메인 실행 스크립트
├── ⚙️  config.py                  # 설정 관리
├── 📋 requirements.txt           # Python 의존성
├── 📝 env.example               # 환경변수 예시
├── 📚 README.md                 # 프로젝트 문서
├── 🔧 setup.py                  # 설치 스크립트
├── 🧪 run_example.py            # 테스트 스크립트
├── 🎭 demo.py                   # 이 데모 스크립트
├── 📁 collectors/               # 데이터 수집기
│   ├── __init__.py
│   ├── base.py                  # 베이스 컬렉터 클래스
│   └── cryptoquant.py           # CryptoQuant API 클라이언트
├── 📁 database/                 # 데이터베이스 관련
│   ├── __init__.py
│   ├── models.py                # Pydantic 데이터 모델
│   └── supabase_client.py       # Supabase 클라이언트
├── 📁 utils/                    # 유틸리티
│   ├── __init__.py
│   └── logger.py                # 로깅 설정
└── 📁 logs/                     # 로그 파일 (자동 생성)
    └── collector.log
    """
    
    print(structure)

def demo_configuration():
    """설정 데모"""
    print("\n⚙️  설정 파일 데모")
    print("=" * 50)
    
    print("📄 config.py - 주요 설정:")
    print("  - SUPABASE_URL: Supabase 프로젝트 URL")
    print("  - SUPABASE_SERVICE_ROLE_KEY: Service Role 키")
    print("  - CRYPTOQUANT_API_KEY: CryptoQuant API 키")
    print("  - RATE_LIMIT_REQUESTS_PER_MINUTE: 10 (무료 플랜)")
    print("  - DEFAULT_DAYS: 7")
    print("  - BATCH_SIZE: 100")
    
    print("\n📄 .env 파일 예시:")
    env_example = """
SUPABASE_URL=https://goeqmhurrhgwmazaxfpm.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
CRYPTOQUANT_API_KEY=your_cryptoquant_api_key_here
    """
    print(env_example)

def demo_database_schema():
    """데이터베이스 스키마 데모"""
    print("\n🗄️  데이터베이스 스키마 데모")
    print("=" * 50)
    
    print("📊 주요 테이블:")
    print("  🪙 cryptocurrencies - 코인 마스터 데이터")
    print("  📈 onchain_metrics - 온체인 메트릭 (CryptoQuant)")
    print("  😊 sentiment_metrics - 감성 분석 데이터")
    print("  📊 derivatives_metrics - 파생상품 데이터")
    print("  🎯 dispersion_scores - 통합 분산도 점수")
    
    print("\n📋 onchain_metrics 주요 필드:")
    print("  - exchange_netflow: 거래소 순유출입")
    print("  - exchange_reserve: 거래소 잔고")
    print("  - active_addresses: 활성 주소 수")
    print("  - miner_netflow: 채굴자 순유출입 (BTC만)")
    print("  - transaction_count: 트랜잭션 수")
    print("  - transaction_volume: 트랜잭션 볼륨")

def demo_usage():
    """사용법 데모"""
    print("\n🚀 사용법 데모")
    print("=" * 50)
    
    print("1️⃣ 환경 설정:")
    print("   pip install -r requirements.txt")
    print("   cp env.example .env")
    print("   # .env 파일에 API 키 설정")
    
    print("\n2️⃣ Supabase 데이터베이스 설정:")
    print("   # Supabase Dashboard → SQL Editor")
    print("   # supabase-dispersion-schema.sql 실행")
    
    print("\n3️⃣ 기본 실행:")
    print("   python main.py --symbol BTC --days 7")
    
    print("\n4️⃣ 고급 옵션:")
    print("   python main.py --symbol ETH --days 3 --interval 4hour")
    print("   python main.py --list-symbols")
    print("   python main.py --test-connection")
    print("   python main.py --symbol BTC --days 1 --dry-run")
    
    print("\n5️⃣ 테스트:")
    print("   python run_example.py")

def demo_data_flow():
    """데이터 플로우 데모"""
    print("\n🔄 데이터 플로우 데모")
    print("=" * 50)
    
    flow_steps = [
        "1. 환경변수 로드 (.env 파일)",
        "2. Supabase 연결 테스트",
        "3. 코인 심볼 → crypto_id 조회",
        "4. CryptoQuant API에서 데이터 수집",
        "   - 거래소 넷플로우",
        "   - 거래소 잔고",
        "   - 활성 주소 수",
        "   - 채굴자 넷플로우 (BTC만)",
        "   - 트랜잭션 데이터",
        "5. Pydantic 모델로 데이터 검증",
        "6. Supabase에 배치 삽입 (upsert)",
        "7. 로그 기록 및 결과 출력"
    ]
    
    for step in flow_steps:
        print(f"  {step}")

def demo_api_endpoints():
    """API 엔드포인트 데모"""
    print("\n🌐 CryptoQuant API 엔드포인트 데모")
    print("=" * 50)
    
    endpoints = [
        ("거래소 넷플로우", "/btc/exchange-flows/netflow"),
        ("거래소 잔고", "/btc/exchange-flows/reserve"),
        ("활성 주소", "/btc/network-data/active-addresses"),
        ("채굴자 넷플로우", "/btc/miner-flows/netflow"),
        ("트랜잭션 수", "/btc/network-data/transaction-count"),
        ("트랜잭션 볼륨", "/btc/network-data/transaction-volume")
    ]
    
    for name, endpoint in endpoints:
        print(f"  📊 {name:15} : {endpoint}")

def demo_error_handling():
    """에러 처리 데모"""
    print("\n⚠️  에러 처리 데모")
    print("=" * 50)
    
    errors = [
        ("API 키 누락", "Missing required environment variables"),
        ("Supabase 연결 실패", "❌ Supabase 연결 실패"),
        ("코인을 찾을 수 없음", "코인을 찾을 수 없습니다: INVALID_SYMBOL"),
        ("Rate Limit 초과", "API 호출 실패: 429"),
        ("데이터 변환 실패", "데이터 변환 실패: {record}"),
        ("저장 실패", "❌ 데이터 저장 실패")
    ]
    
    for error_type, message in errors:
        print(f"  🚨 {error_type:15} : {message}")

def demo_logging():
    """로깅 데모"""
    print("\n📝 로깅 시스템 데모")
    print("=" * 50)
    
    print("📁 로그 파일: logs/collector.log")
    print("📊 로그 레벨: INFO (DEBUG, INFO, WARNING, ERROR)")
    
    print("\n📋 로그 내용:")
    log_examples = [
        "2025-01-26 10:00:00 - INFO - Starting CryptoQuant data collection...",
        "2025-01-26 10:00:05 - INFO - API 호출 성공: /btc/exchange-flows/netflow - 200 (1.23s)",
        "2025-01-26 10:00:10 - INFO - 데이터 수집 완료: BTC - 168개 레코드 (5.67s)",
        "2025-01-26 10:00:15 - INFO - 온체인 메트릭 168개 레코드 삽입 완료",
        "2025-01-26 10:00:15 - INFO - ✅ 데이터 저장 완료"
    ]
    
    for log in log_examples:
        print(f"  {log}")

def main():
    """메인 데모 함수"""
    print("🎭 Dispersion Signal 프로젝트 데모")
    print("=" * 60)
    print("이 데모는 실제 API 키 없이도 프로젝트의 구조와 기능을 확인할 수 있습니다.")
    print("=" * 60)
    
    demos = [
        ("프로젝트 구조", demo_project_structure),
        ("설정 파일", demo_configuration),
        ("데이터베이스 스키마", demo_database_schema),
        ("사용법", demo_usage),
        ("데이터 플로우", demo_data_flow),
        ("API 엔드포인트", demo_api_endpoints),
        ("에러 처리", demo_error_handling),
        ("로깅 시스템", demo_logging),
    ]
    
    for demo_name, demo_func in demos:
        demo_func()
        print()  # 빈 줄 추가
    
    print("🎉 데모 완료!")
    print("\n📚 다음 단계:")
    print("1. .env 파일에 실제 API 키 설정")
    print("2. Supabase 데이터베이스 스키마 생성")
    print("3. python run_example.py 실행하여 테스트")
    print("4. python main.py --symbol BTC --days 7 실행")

if __name__ == "__main__":
    main()
