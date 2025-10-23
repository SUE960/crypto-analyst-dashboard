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

Vercel에 배포하려면:

1. GitHub에 프로젝트 푸시
2. Vercel에서 프로젝트 연결
3. 환경 변수 설정
4. 배포 완료

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
