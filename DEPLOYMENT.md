# Vercel 배포 설정

## 배포 방법

### 1. Vercel 웹 대시보드를 통한 배포 (권장)

1. [Vercel.com](https://vercel.com)에 접속하여 GitHub 계정으로 로그인
2. "New Project" 클릭
3. GitHub 저장소 `SUE960/crypto-analyst-dashboard` 선택
4. 프로젝트 설정:
   - **Framework Preset**: Next.js
   - **Root Directory**: `./` (기본값)
   - **Build Command**: `npm run build` (기본값)
   - **Output Directory**: `.next` (기본값)
   - **Install Command**: `npm install` (기본값)

5. 환경 변수 설정:
   - `NEXT_PUBLIC_SUPABASE_URL`: `https://goeqmhurrhgwmazaxfpm.supabase.co`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: `your_supabase_anon_key_here`

6. "Deploy" 클릭

### 2. Vercel CLI를 통한 배포

```bash
# Vercel CLI 설치
npm install -g vercel

# 로그인
vercel login

# 배포
vercel --prod
```

### 3. GitHub Actions를 통한 자동 배포

프로젝트에 이미 `.github/workflows/deploy.yml` 파일이 포함되어 있어서
GitHub에 푸시할 때마다 자동으로 배포됩니다.

## 배포 후 설정

1. **Supabase API 키 설정**:
   - Vercel 대시보드 → Project Settings → Environment Variables
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` 추가

2. **도메인 설정**:
   - Vercel에서 제공하는 기본 도메인 사용 또는 커스텀 도메인 연결

3. **데이터베이스 설정**:
   - 배포된 사이트의 `/api/supabase-setup` 엔드포인트 호출
   - 또는 Supabase 대시보드에서 직접 SQL 실행

## 배포 상태 확인

배포가 완료되면 다음 URL에서 확인할 수 있습니다:
- Vercel 기본 도메인: `https://crypto-analyst-dashboard-xxx.vercel.app`
- 커스텀 도메인: 설정한 도메인
