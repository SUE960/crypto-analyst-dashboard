# Crypto Analyst Dashboard - 분석 계획서

## Team Chris 프로젝트

**프로젝트 목표**: 애널리스트·인플루언서 의견 분산과 코인가격 변동의 상관관계를 분석하고, 향후 유망 코인을 추천하는 서비스 구축

---

## 📊 분석 개요

### 기준 설정
- **기간**: 2021.01 - 2025.08
- **데이터 주기**: 일 단위 또는 시간 단위
- **분석 단위**: 코인별 일간 데이터 기준 (Daily Granularity)

### 최종 목표
1. **코인별 의견-가격 상관계수** 분석
2. **감성지수 기반 예측모델** 구축
3. **추천 점수 및 Top N 리스트** 제공

---

## 🎯 코인 선정 기준

| 항목 | 기준 |
|------|------|
| **선정 개수** | 상위 20~30개 (시가총액 기준) |
| **선정 조건** | - CoinGecko 기준 시가총액 Top 30<br>- 거래소(Upbit, Binance) 양쪽 상장<br>- 3년 이상 거래 데이터 확보 가능 |
| **예시 리스트** | BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOGE, DOT, MATIC, LINK, ARB, OP, APT, SUI 등 |

---

## 📈 데이터 수집 기준

### 1. 애널리스트 리포트

| 항목 | 기준 |
|------|------|
| **출처** | Messari, CoinDesk, Glassnode, Binance Research 등 |
| **수집 주기** | 주단위 (Weekly) |
| **필터링 기준** | 동일 애널리스트 1주 1건 / 중복 목표가 제거 |
| **메타데이터 포함** | 출처, 작성일, 목표가, 기준가격, 신뢰도(과거 정확도 기반) |

### 2. 인플루언서 (X, Reddit)

| 항목 | 기준 |
|------|------|
| **출처** | X(Twitter), Reddit (r/CryptoCurrency, r/Bitcoin 등) |
| **수집 방식** | API + 크롤러 |
| **수집 주기** | 일단위 (Daily) |
| **필터링 기준** | - 팔로워 10k 이상<br>- 특정 코인 키워드 포함<br>- 리트윗/좋아요 수 50 이상 |
| **감성분석** | Transformer 기반 다국어 감성모델 (예: FinBERT, KoBERT, RoBERTa) |

### 3. 커뮤니티 (DeFi / APY)

| 항목 | 기준 |
|------|------|
| **출처** | DeFiLlama, Aave Forum, Curve Governance Forum 등 |
| **수집 주기** | 주단위 (Weekly Snapshot) |
| **포함 항목** | 예측가, TVL(총예치금), APR/수익률, 언급량 |
| **정제 기준** | 특정 코인 언급량 3건 이상일 때만 유효 |

### 4. 매크로 변수

| 항목 | 기준 |
|------|------|
| **출처** | FRED, IMF, Yahoo Finance, 경제일정 캘린더 |
| **수집 항목** | CPI, 금리, 유동성지표, VIX, 달러인덱스, BTC 도미넌스 |
| **이벤트 데이터화** | 이벤트 발생일 ±7일 dummy 변수 생성 |

### 5. 종속변수 (가격)

| 항목 | 기준 |
|------|------|
| **출처** | CoinGecko API, Binance API |
| **수집 항목** | 종가, 거래량, 시가총액, 변동률 |
| **수집 주기** | 일단위 |
| **기간** | 동일하게 2022–2025년 |
| **결측치 처리** | Linear interpolation 또는 최근값 보간 |

---

## 🗄️ 데이터베이스 스키마 설계

### 1. 애널리스트 데이터

| 필드명 | 타입 | 설명 |
|--------|------|------|
| `analyst_id` | UUID | 애널리스트 고유 식별자 |
| `analyst_name` | VARCHAR(100) | 애널리스트 이름 |
| `source` | VARCHAR(50) | 출처 (CoinDesk, Messari 등) |
| `coin_name` | VARCHAR(20) | 분석 대상 코인명 (BTC, ETH 등) |
| `target_price` | DECIMAL(20,8) | 제시된 목표가 |
| `current_price` | DECIMAL(20,8) | 기준가격 |
| `report_date` | DATE | 보고서 발표일 |
| `sentiment` | VARCHAR(20) | 긍정/중립/부정 등 의견 분류 |
| `reliability_score` | DECIMAL(3,2) | 과거 예측 정확도 기반 신뢰도 점수 |
| `created_at` | TIMESTAMP | 데이터 생성일시 |

### 2. 인플루언서 의견 데이터

| 필드명 | 타입 | 설명 |
|--------|------|------|
| `influencer_id` | UUID | 인플루언서 고유 ID (SNS 계정 기준) |
| `influencer_name` | VARCHAR(100) | 인플루언서 이름/핸들 |
| `platform` | VARCHAR(20) | 출처 (Twitter/X, Reddit 등) |
| `coin_name` | VARCHAR(20) | 언급된 코인명 |
| `content` | TEXT | 게시글 내용 |
| `sentiment_score` | DECIMAL(3,2) | 감성 분석 결과 (-1~1 점수) |
| `engagement` | INTEGER | 반응지표 (좋아요, 리트윗, 댓글 등) |
| `post_date` | TIMESTAMP | 작성일시 |
| `created_at` | TIMESTAMP | 데이터 생성일시 |

### 3. 커뮤니티 데이터 (DeFi / Forum)

| 필드명 | 타입 | 설명 |
|--------|------|------|
| `user_id` | UUID | 작성자 ID |
| `user_name` | VARCHAR(100) | 작성자 이름 |
| `platform` | VARCHAR(50) | 출처 (DeFiLlama, Aave Forum 등) |
| `coin_name` | VARCHAR(20) | 언급된 코인명 |
| `predicted_price` | DECIMAL(20,8) | 사용자 또는 커뮤니티에서 언급된 예측가 |
| `post_date` | TIMESTAMP | 작성일 |
| `upvote_count` | INTEGER | 추천 수 등 신뢰도 지표 |
| `created_at` | TIMESTAMP | 데이터 생성일시 |

### 4. 매크로 이벤트 데이터

| 필드명 | 타입 | 설명 |
|--------|------|------|
| `macro_event_id` | UUID | 이벤트 ID |
| `macro_event_name` | VARCHAR(200) | 이벤트명 (CPI 발표, 금리 결정 등) |
| `event_date` | DATE | 발생일 |
| `event_type` | VARCHAR(50) | 구분 (금융정책, 지정학, 규제, 기술 등) |
| `expected_impact` | DECIMAL(3,2) | 예측 영향도 (+/-) |
| `actual_impact` | DECIMAL(3,2) | 실제 시장 반응 지표 |
| `created_at` | TIMESTAMP | 데이터 생성일시 |

### 5. 코인 가격 데이터

| 필드명 | 타입 | 설명 |
|--------|------|------|
| `coin_id` | UUID | 코인 고유 ID |
| `coin_name` | VARCHAR(20) | 코인명 |
| `symbol` | VARCHAR(10) | 코인 심볼 (BTC, ETH 등) |
| `price` | DECIMAL(20,8) | 종가 또는 시가 |
| `volume` | BIGINT | 거래량 |
| `market_cap` | BIGINT | 시가총액 |
| `price_change_24h` | DECIMAL(20,8) | 24시간 가격 변동 |
| `price_change_percentage_24h` | DECIMAL(10,4) | 24시간 가격 변동률 |
| `date` | DATE | 날짜 |
| `source` | VARCHAR(50) | 데이터 출처 (CoinGecko, Binance API 등) |
| `created_at` | TIMESTAMP | 데이터 생성일시 |

---

## 🔬 분석/모델링 기준

| 항목 | 기준 |
|------|------|
| **상관분석** | 피어슨, 스피어만 상관계수 (r, ρ) |
| **시계열 분석** | Granger Causality Test (원인성 검정) |
| **예측 모델** | LSTM / Transformer 기반 시계열 예측 모델 |
| **평가지표** | RMSE, MAE, R² (회귀), Accuracy/F1 (상관 방향 분류) |
| **추천 산식** | `Score(c) = α₁Ŷₜ₊₁(c) + α₂Sentimentₜ(c) + α₃Reliabilityₜ(c)` |

---

## 🚀 서비스 운영 기준

| 항목 | 기준 |
|------|------|
| **갱신 주기** | 하루 1회 자동 업데이트 |
| **추천 대상** | 상위 10개 코인 |
| **추천 근거 표출** | "긍정 의견 72%, 애널리스트 목표가 평균 +12% 상향, 가격변동 +3% 예측" 형태로 시각화 |
| **신뢰도 지표** | 표준편차가 작고, 다수 출처 의견이 일치할수록 점수 ↑ |
| **UI 구성** | 코인명 / 현재가 / 추천점수 / 긍정비율 / 주요 이벤트 |

---

## 🛠️ 기술 스택

| 항목 | 기술 |
|------|------|
| **데이터 저장소** | PostgreSQL (정형) + MongoDB (비정형) |
| **API 구성** | FastAPI 기반 REST API |
| **프론트엔드** | Next.js + React + Chart.js 기반 대시보드 |
| **스케줄러** | Airflow 또는 Celery |
| **서버 환경** | Vercel (프론트엔드) + AWS EC2 (백엔드/모델) |
| **버전 관리** | GitHub + DVC (데이터 버전 관리) |

---

## 📋 데이터 전처리 기준

| 항목 | 기준 |
|------|------|
| **텍스트 정제** | URL, 해시태그, 이모지, 특수문자 제거 |
| **감성지수 스케일** | -1 ~ +1 범위 정규화 |
| **시간정렬** | UTC 기준으로 모든 데이터 동기화 |
| **이상치 처리** | 3σ 이상 편차값 제거 또는 Winsorization |
| **ID 정합성** | 코인명은 CoinGecko ID 기반 통일 (예: bitcoin, ethereum 등) |

---

## 🎯 훈련/검증/테스트 분리

| 구분 | 기간 | 목적 |
|------|------|------|
| **Train** | 2022~2023년 | 모델 훈련 |
| **Validation** | 2024년 | 하이퍼파라미터 튜닝 |
| **Test** | 2025년 | 최종 성능 평가 |

---

## 📊 핵심 지표

### 상관관계 분석
- 애널리스트 목표가와 실제 가격 변동의 상관계수
- 인플루언서 감성지수와 가격 변동의 상관계수
- 커뮤니티 예측과 실제 결과의 정확도

### 예측 모델 성능
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)
- R² (결정계수)
- Accuracy/F1 Score (방향성 예측)

### 추천 시스템
- 추천 정확도 (Top-N Precision)
- 사용자 만족도 지표
- 실시간 업데이트 성능

---

## 🔄 개발 로드맵

### Phase 1: 데이터 수집 인프라 구축
- [ ] API 연동 (CoinGecko, Binance, Twitter API 등)
- [ ] 데이터베이스 스키마 구현
- [ ] 기본 데이터 수집 파이프라인 구축

### Phase 2: 분석 모델 개발
- [ ] 감성 분석 모델 구축
- [ ] 상관관계 분석 구현
- [ ] 예측 모델 개발

### Phase 3: 서비스 배포
- [ ] 웹 대시보드 개발
- [ ] API 서버 구축
- [ ] 자동화 시스템 구축

### Phase 4: 성능 최적화
- [ ] 모델 성능 개선
- [ ] 실시간 데이터 처리 최적화
- [ ] 사용자 경험 개선

---

**Team Chris** - 암호화폐 시장 분석 및 추천 서비스 개발팀

