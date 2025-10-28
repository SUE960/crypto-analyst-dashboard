# Dispersion Signal - CryptoQuant 데이터 수집기

암호화폐 온체인 데이터를 수집하여 분산도 신호를 분석하는 시스템의 데이터 수집 모듈입니다.

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp env.example .env
# .env 파일을 편집하여 API 키 설정
```

### 2. Supabase 데이터베이스 설정

1. Supabase Dashboard → SQL Editor 이동
2. `supabase-dispersion-schema.sql` 파일의 내용을 복사하여 실행
3. 테이블 생성 및 기본 데이터 삽입 확인

### 3. 실행

```bash
# 비트코인 최근 7일 데이터 수집
python main.py --symbol BTC --days 7

# 사용 가능한 코인 목록 확인
python main.py --list-symbols

# 연결 테스트
python main.py --test-connection

# 드라이 런 (실제 저장 없이 테스트)
python main.py --symbol BTC --days 1 --dry-run
```

## 📁 프로젝트 구조

```
dispersion_signal/
├── main.py                    # 메인 실행 스크립트
├── config.py                  # 설정 관리
├── requirements.txt           # Python 의존성
├── env.example               # 환경변수 예시
├── collectors/               # 데이터 수집기
│   ├── __init__.py
│   ├── base.py              # 베이스 컬렉터 클래스
│   └── cryptoquant.py       # CryptoQuant API 클라이언트
├── database/                 # 데이터베이스 관련
│   ├── __init__.py
│   ├── models.py            # Pydantic 데이터 모델
│   └── supabase_client.py   # Supabase 클라이언트
├── utils/                    # 유틸리티
│   ├── __init__.py
│   └── logger.py            # 로깅 설정
└── logs/                     # 로그 파일
    └── collector.log
```

## 🔧 설정

### 환경변수

`.env` 파일에 다음 변수들을 설정하세요:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
CRYPTOQUANT_API_KEY=your_cryptoquant_api_key
```

### API 키 발급

1. **CryptoQuant API**: [cryptoquant.com](https://cryptoquant.com)에서 무료 계정 생성
2. **Supabase**: 프로젝트 설정에서 Service Role Key 복사

## 📊 수집되는 데이터

### 온체인 메트릭 (CryptoQuant)

- **거래소 플로우**: 넷플로우, 유입량, 유출량, 잔고
- **활성 주소**: 일일 활성 주소 수
- **트랜잭션**: 수량, 볼륨
- **채굴자 플로우**: 채굴자 넷플로우 (Bitcoin만)

## 🛠️ 사용법

### 명령행 옵션

```bash
python main.py [옵션]

옵션:
  --symbol SYMBOL      수집할 코인 심볼 (기본값: BTC)
  --days DAYS          수집할 일수 (기본값: 7)
  --interval INTERVAL  데이터 간격 (1hour, 4hour, 1day)
  --list-symbols       사용 가능한 코인 목록 출력
  --test-connection    Supabase 연결 테스트만 실행
  --dry-run            실제 저장 없이 수집만 테스트
```

### 예시

```bash
# 비트코인 최근 3일 데이터 수집
python main.py --symbol BTC --days 3

# 이더리움 4시간 간격으로 7일 데이터 수집
python main.py --symbol ETH --days 7 --interval 4hour

# 드라이 런으로 데이터 수집 테스트
python main.py --symbol SOL --days 1 --dry-run
```

## 📈 로그

로그는 `logs/collector.log` 파일에 저장되며, 다음 정보를 포함합니다:

- API 호출 상태 및 응답 시간
- 데이터 수집 진행 상황
- 에러 및 예외 정보
- 저장된 레코드 수

## 🔍 문제 해결

### 일반적인 문제

1. **API 키 오류**
   ```
   Missing required environment variables: CRYPTOQUANT_API_KEY
   ```
   → `.env` 파일에 올바른 API 키가 설정되었는지 확인

2. **Supabase 연결 실패**
   ```
   ❌ Supabase 연결 실패
   ```
   → Supabase URL과 Service Role Key가 올바른지 확인

3. **코인을 찾을 수 없음**
   ```
   코인을 찾을 수 없습니다: INVALID_SYMBOL
   ```
   → `--list-symbols`로 사용 가능한 코인 목록 확인

4. **Rate Limit 초과**
   ```
   API 호출 실패: 429
   ```
   → CryptoQuant 무료 플랜은 10 requests/분 제한

### 디버깅

```bash
# 상세 로그와 함께 실행
python main.py --symbol BTC --days 1 --dry-run

# 로그 파일 확인
tail -f logs/collector.log
```

## 🔄 자동화

### Cron 작업 설정

매 시간마다 데이터 수집:

```bash
# crontab 편집
crontab -e

# 다음 라인 추가 (매 시간 정각에 실행)
0 * * * * cd /path/to/dispersion_signal && python main.py --symbol BTC --days 1
```

### GitHub Actions

`.github/workflows/collect-data.yml`:

```yaml
name: Collect CryptoQuant Data
on:
  schedule:
    - cron: '0 * * * *'  # 매 시간
  workflow_dispatch:

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: |
          pip install -r requirements.txt
          python main.py --symbol BTC --days 1
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          CRYPTOQUANT_API_KEY: ${{ secrets.CRYPTOQUANT_API_KEY }}
```

## 📝 라이선스

MIT License

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 지원

문제가 발생하면 GitHub Issues에 보고해주세요.
