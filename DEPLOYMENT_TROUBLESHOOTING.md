# Vercel 자동 배포 설정

## 문제 해결 방법

### 1. Vercel 대시보드에서 직접 배포
1. Vercel 프로젝트 페이지 접속
2. "Deployments" 탭 클릭
3. "Redeploy" 버튼 클릭

### 2. GitHub Actions 수동 실행
1. GitHub 저장소 → Actions 탭
2. "Deploy to Vercel" 워크플로우 선택
3. "Run workflow" 버튼 클릭

### 3. Vercel CLI로 직접 배포
```bash
npx vercel --prod --yes
```

### 4. 환경 변수 확인
Vercel 프로젝트 설정에서 다음 환경 변수가 설정되어 있는지 확인:
- `NEXT_PUBLIC_SUPABASE_URL`: https://goeqmhurrhgwmazaxfpm.supabase.co
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: your_supabase_anon_key

### 5. 프로젝트 ID 확인
현재 프로젝트 ID: `prj_RmAsjaCZKR2urUZxuS3uaawXYNpD`

## 즉시 해결 방법
가장 빠른 방법은 Vercel 대시보드에서 "Redeploy" 버튼을 클릭하는 것입니다.
