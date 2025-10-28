# Crypto Analyst Dashboard

**Team Chris** 프로젝트 - 코인 분석가 목표가와 트윗 감정 분석을 통한 암호화폐 추천 서비스

## 🎯 프로젝트 목표

애널리스트·인플루언서 의견 분산과 코인가격 변동의 상관관계를 분석하고, 향후 유망 코인을 추천하는 서비스를 구축합니다.

## 📊 주요 기능

- 📊 **실시간 코인 가격 추적**: 주요 암호화폐의 가격 변화를 실시간으로 모니터링
- 🎯 **애널리스트 목표가 분석**: 전문가들의 목표가 예측과 정확도 분석
- 💬 **소셜 미디어 감정 분석**: 트위터 인플루언서들의 의견과 감정 분석
- 📈 **상관성 분석**: 애널리스트 의견, 감정, 가격 간의 상관관계 분석
- 🎨 **현대적인 다크 테마 UI**: 어두운 테마의 직관적인 사용자 인터페이스
- 🤖 **AI 기반 추천 시스템**: 감성분석과 예측모델을 통한 코인 추천

## 🛠️ 기술 스택

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS, Radix UI
- **Charts**: Recharts
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Vercel
- **AI/ML**: Python, TensorFlow, PyTorch (예정)
- **Data Collection**: APIs (CoinGecko, Binance, Twitter), Web Scraping

## 설치 및 실행

1. 의존성 설치:
```bash
npm install
```

2. 환경 변수 설정:
```bash
cp .env.local.example .env.local
```

`.env.local` 파일에 Supabase 설정을 추가하세요:
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

3. 개발 서버 실행:
```bash
npm run dev
```

4. 브라우저에서 [http://localhost:3000](http://localhost:3000) 접속

## 데이터베이스 설정

Supabase에서 `supabase-schema.sql` 파일의 SQL을 실행하여 데이터베이스 스키마를 생성하세요.

## 배포

Vercel
https://crypto-analyst-dashboard-akm5fo5ci-jisukangs-projects-3044b26f.vercel.app/

## 📋 프로젝트 문서

- [분석 계획서](./ANALYSIS_PLAN.md) - 상세한 데이터 수집 및 분석 계획
- [배포 가이드](./DEPLOYMENT.md) - Vercel 배포 설정 방법
- [문제 해결 가이드](./DEPLOYMENT_TROUBLESHOOTING.md) - 배포 관련 문제 해결

## 👥 Team Chris

**암호화폐 시장 분석 및 추천 서비스 개발팀**

- 프로젝트 관리 및 기획
- 데이터 수집 및 분석 시스템 구축
- AI/ML 모델 개발
- 웹 서비스 개발 및 배포

## 라이선스

MIT License


## 📚 프로젝트 요약 (요약 정리)

이 레포는 암호화폐 추천을 위한 프론트엔드 대시보드(Next.js)와 데이터 수집·분석 파이프라인(Python)로 구성됩니다. 애널리스트 목표가, 인플루언서/커뮤니티 감성, 가격 데이터의 상관관계를 분석하여 유망 코인을 제안하는 것을 목표로 합니다.

### 구성 요소 한눈에 보기

- **웹 앱 (Next.js 14, React 18, TypeScript)**
  - UI 컴포넌트: `components/` 디렉터리의 카드, 차트, 탭 등 재사용 컴포넌트
  - API 라우트: `app/api/*/route.ts`로 서버리스 함수 제공 (코인 세부, 커뮤니티/인플루언서, 소셜 트렌드 등)
  - Supabase 연동: `lib/supabase.ts`, `lib/supabase-setup.ts`, `lib/seed.ts`
- **데이터 파이프라인 (Python, `dispersion_signal/`)**
  - 수집기: `collectors/` (CoinGecko, Binance, CryptoCompare, Reddit, Twitter 대체 등)
  - 데이터 품질/보안: `utils/data_quality.py`, `utils/security.py`, `utils/monitoring.py`
  - DB 모델/클라이언트: `database/models_*.py`, `database/supabase_client_*.py`
  - 실행 엔트리포인트: `main_*.py` 스크립트 (phase2~4, coingecko, binance, analyst_targets 등)

### 데이터베이스 스키마

`supabase-*.sql` 파일들에 단계별 테이블·인덱스가 정의되어 있습니다. 초기에는 `supabase-schema.sql` 또는 목적별 스키마 파일을 Supabase SQL Editor에서 실행합니다. 성능 관련 인덱스/머티리얼라이즈드 뷰 아이디어는 `database-optimization.sql`에 정리되어 있습니다.

### 주요 스크립트

- `dispersion_signal/main.py`: 기본 파이프라인 실행 예시
- `dispersion_signal/main_coingecko.py`, `main_binance.py`: 거래소/시세 데이터 수집
- `dispersion_signal/main_analyst_targets.py`: 애널리스트 목표가 파이프라인
- `dispersion_signal/main_phase2.py` ~ `main_phase4.py`: 단계별 확장 분석
- `dispersion_signal/run_example.py`, `demo.py`: 사용 예시

## 🚀 로컬 실행 가이드 (보완)

### 1) 프론트엔드

1. 의존성 설치: `npm install`
2. 환경 변수: `.env.local`에 `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` 설정
3. 개발 서버: `npm run dev` 후 `http://localhost:3000` 접속

### 2) 데이터 파이프라인 (Python)

1. 가상환경 생성 및 활성화
   - macOS/Linux
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
2. 의존성 설치
   ```bash
   pip install -r dispersion_signal/requirements.txt
   ```
3. 환경 변수
   - `dispersion_signal/env.example` 참고하여 필요한 키를 셋업 (예: API 키, Supabase URL/Key)
4. 예시 실행
   ```bash
   python dispersion_signal/run_example.py
   ```
5. 수집/분석 실행
   ```bash
   python dispersion_signal/main_coingecko.py
   python dispersion_signal/main_binance.py
   python dispersion_signal/main_analyst_targets.py
   ```

## 🔌 API 엔드포인트 개요 (요약)

- `app/api/coin/[symbol]/route.ts`: 심볼별 코인 상세/차트 데이터
- `app/api/community/route.ts`: 커뮤니티/커멘트 데이터 요약
- `app/api/influencer/route.ts`: 인플루언서 포스트/감성 요약
- `app/api/social-trends/route.ts`: 소셜 트렌드 지표
- `app/api/data/route.ts`: 통합 데이터 핸들러 (필요 시 확장)
- `app/api/seed/route.ts`, `app/api/supabase-setup/route.ts`: 초기화/시드 스크립트

## 🧪 문제 해결 체크리스트 (에러 원인과 해결)

- **프론트 서버가 500/환경변수 오류**
  - 원인: `.env.local`의 `NEXT_PUBLIC_SUPABASE_URL/ANON_KEY` 미설정 또는 오타
  - 해결: `.env.local` 재확인, 빌드 캐시 제거(`rm -rf .next`) 후 `npm run dev` 재실행

- **Supabase 인증/권한 에러 (RLS 관련 401/403)**
  - 원인: 테이블 RLS 정책 미설정, 서비스 롤키/Anon 키 사용 혼동
  - 해결: 스키마 실행 후 RLS 정책 확인, 서버사이드에서 필요한 경우 서비스 롤키 사용

- **데이터 수집 스크립트 실행 실패 (ModuleNotFoundError, ImportError)**
  - 원인: 가상환경 미활성화, 의존성 누락
  - 해결: `.venv` 활성화 후 `pip install -r dispersion_signal/requirements.txt`

- **API Rate Limit / 네트워크 타임아웃**
  - 원인: 외부 데이터 소스 호출 빈도 과다
  - 해결: 백오프/재시도 설정, API 키 발급/업그레이드, 캐시 사용(`dispersion_signal/cache/`)

- **성능 저하/응답 지연**
  - 원인: 인덱스 미비, 불필요한 전체 스캔
  - 해결: `database-optimization.sql` 참고하여 인덱스/뷰 적용, N+1 쿼리 점검

- **배포 시 환경변수 누락 (Vercel 500/Build 실패)**
  - 원인: Vercel 프로젝트의 Environment Variables 미설정
  - 해결: Vercel Dashboard → Settings → Environment Variables에 동일 키 추가 후 재배포

## 🗺️ 로드맵 (Next)

- 추천 모델 강화: 시그널 분산지표 + 감성스코어 융합 모델
- 대시보드 고급 차트: Recharts 커스텀 툴팁/줌, 멀티축 상관 차트
- 알림/구독: 신호 임계치 도달 시 알림
- 데이터 신뢰도: 수집 실패 감지/자동 재시도 + 데이터 품질 리포트
- 운영 자동화: 백업/모니터링 워크플로우, 스케줄러 정식 도입
