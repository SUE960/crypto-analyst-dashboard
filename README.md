# Crypto Analyst Dashboard

코인 분석가 목표가와 트윗 감정 분석을 통한 암호화폐 추천 서비스

## 기능

- 📊 **실시간 코인 가격 추적**: 주요 암호화폐의 가격 변화를 실시간으로 모니터링
- 🎯 **애널리스트 목표가 분석**: 전문가들의 목표가 예측과 정확도 분석
- 💬 **소셜 미디어 감정 분석**: 트위터 인플루언서들의 의견과 감정 분석
- 📈 **상관성 분석**: 애널리스트 의견, 감정, 가격 간의 상관관계 분석
- 🎨 **현대적인 다크 테마 UI**: 어두운 테마의 직관적인 사용자 인터페이스

## 기술 스택

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS, Radix UI
- **Charts**: Recharts
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Vercel

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

## 라이선스

MIT License
