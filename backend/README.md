# JobPilot Backend API

FastAPI 기반의 취업 준비생 관심기업 브리핑 서비스 백엔드입니다.

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# .env 파일 생성
cp .env.example .env

# PostgreSQL 시작
docker-compose up -d postgres
```

### 2. 의존성 설치

```bash
# uv 사용 (권장)
uv sync

# 또는 poetry
poetry install

# 또는 pip
pip install -r requirements.txt
```

### 3. 데이터베이스 초기화

```bash
# 마이그레이션 실행 (006 migration까지 포함)
alembic upgrade head

# 테스트 데이터 생성
python -m app.scripts.seed
```

### 4. 서버 실행

```bash
# PM2로 실행 (백그라운드)
pm2 start ecosystem.config.cjs

# 또는 직접 실행 (개발 모드)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📡 API 엔드포인트

### Health Check
```bash
GET /health
```

### Companies (기업)
```bash
# 기업 목록
GET /api/v1/companies?q={검색어}&company_type={LARGE|MID|PUBLIC}&limit=20&offset=0

# 기업 상세 (최신 prep_snapshot 포함)
GET /api/v1/companies/{company_id}

# 기업별 최신 뉴스
GET /api/v1/companies/{company_id}/news?limit=20&offset=0

# 기업별 채용공고 (OPEN 우선, 게시일 최신순)  ← Phase 3 신규
GET /api/v1/companies/{company_id}/jobs?limit=20&offset=0
```

### Auth (인증)
```bash
# 회원가입
POST /api/v1/auth/signup
Body: {"email": "user@example.com", "password": "password1234", "nickname": "닉네임"}

# 로그인 (JWT access token 발급)
POST /api/v1/auth/login
Body: {"email": "user@example.com", "password": "password1234"}
# Response: {"success": true, "data": {"access_token": "eyJ...", "token_type": "bearer"}}

# 내 프로필 조회 (인증 필요)
GET /api/v1/users/me
Header: Authorization: Bearer <access_token>
```

### Subscriptions (관심기업) – 인증 필요
```bash
# 관심기업 목록 (인증 필요)
GET /api/v1/subscriptions
Header: Authorization: Bearer <access_token>

# 관심기업 추가 (인증 필요)
POST /api/v1/subscriptions
Header: Authorization: Bearer <access_token>
Body: {"company_id": 1, "memo": "메모"}

# 관심기업 삭제 (인증 필요)
DELETE /api/v1/subscriptions/{subscription_id}
Header: Authorization: Bearer <access_token>
```

### Briefings (브리핑) – 인증 필요
```bash
# 오늘의 브리핑 (인증 필요)
GET /api/v1/briefings/today
Header: Authorization: Bearer <access_token>
```

---

## ⚙️ 배치 스크립트

### Phase 1 – 뉴스 수집
```bash
# 전체 관심기업 뉴스 수집
python -m app.scripts.news.collect_news

# 특정 기업 수집
python -m app.scripts.news.collect_news --company-id 31

# 미리보기 (저장 없음)
python -m app.scripts.news.collect_news --dry-run

# 기업당 최대 10건
python -m app.scripts.news.collect_news --limit 10
```

### Phase 2 – 브리핑 생성
```bash
# 오늘 브리핑 전체 사용자 생성
python -m app.scripts.briefings.generate_today_briefings

# 특정 사용자만 생성
python -m app.scripts.briefings.generate_today_briefings --user-id 1

# 특정 날짜 브리핑 생성
python -m app.scripts.briefings.generate_today_briefings --date 2026-04-12

# 미리보기 (저장 없음)
python -m app.scripts.briefings.generate_today_briefings --dry-run

# 기존 브리핑 덮어쓰기
python -m app.scripts.briefings.generate_today_briefings --overwrite
```

### Phase 4 – PrepSnapshot 자동 생성
```bash
# 전체 관심기업 snapshot 생성 (오늘 날짜)
python -m app.scripts.prep.generate_prep_snapshots

# 특정 기업만 생성
python -m app.scripts.prep.generate_prep_snapshots --company-id 31

# 미리보기 (저장 없음)
python -m app.scripts.prep.generate_prep_snapshots --dry-run

# 기존 snapshot 덮어쓰기
python -m app.scripts.prep.generate_prep_snapshots --overwrite

# 특정 날짜 지정
python -m app.scripts.prep.generate_prep_snapshots --date 2026-04-14

# 최대 기업 수 제한
python -m app.scripts.prep.generate_prep_snapshots --limit 5
```

### Phase 3 – 채용공고 수집
```bash
# 전체 관심기업 채용공고 수집
python -m app.scripts.jobs.collect_jobs

# 특정 기업 수집
python -m app.scripts.jobs.collect_jobs --company-id 31

# 기업당 최대 10건
python -m app.scripts.jobs.collect_jobs --limit 10

# 미리보기 (저장 없음)
python -m app.scripts.jobs.collect_jobs --dry-run

# 최근 60일 기준
python -m app.scripts.jobs.collect_jobs --days 60
```

### 권장 cron 설정
```cron
# 매일 07:00 뉴스 수집
0 7 * * * cd /home/user/webapp/backend && /home/user/webapp/backend/.venv/bin/python -m app.scripts.news.collect_news >> /var/log/collect_news.log 2>&1

# 매일 07:30 브리핑 생성 (뉴스 수집 30분 후)
30 7 * * * cd /home/user/webapp/backend && /home/user/webapp/backend/.venv/bin/python -m app.scripts.briefings.generate_today_briefings >> /var/log/generate_briefings.log 2>&1

# 매일 08:00 채용공고 수집
0 8 * * * cd /home/user/webapp/backend && /home/user/webapp/backend/.venv/bin/python -m app.scripts.jobs.collect_jobs >> /var/log/collect_jobs.log 2>&1

# 매일 08:30 PrepSnapshot 자동 생성 (뉴스+채용공고 수집 완료 후)
30 8 * * * cd /home/user/webapp/backend && /home/user/webapp/backend/.venv/bin/python -m app.scripts.prep.generate_prep_snapshots >> /var/log/generate_prep_snapshots.log 2>&1
```

---

## 📊 데이터베이스

### 모델 구조

| 모델 | 테이블 | 설명 |
|------|--------|------|
| `User` | `users` | 사용자 정보 |
| `Company` | `companies` | 기업 정보 (이름, 유형, 산업, 요약) |
| `Subscription` | `subscriptions` | 관심기업 등록 (user ↔ company) |
| `PrepSnapshot` | `prep_snapshots` | 기업별 채용 준비 스냅샷 |
| `CompanyNews` | `company_news` | 기업별 수집 뉴스 (Phase 1) |
| `Briefing` | `briefings` | 날짜별 브리핑 – unique(user_id, briefing_date) (Phase 2) |
| `BriefingItem` | `briefing_items` | 브리핑 아이템 (뉴스 기반) (Phase 2) |
| `CompanyJobPosting` | `company_job_postings` | 기업별 채용공고 스냅샷 (Phase 3) |
| `PrepSnapshot` (확장) | `prep_snapshots` | 기업 준비 카드 – auto_batch 생성 지원 (Phase 4) |

### 마이그레이션 히스토리

| 버전 | 파일 | 내용 |
|------|------|------|

# ─── Phase 5: JWT Authentication ────
SECRET_KEY=CHANGE_ME_IN_PRODUCTION_USE_STRONG_RANDOM_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
| 001 | `001_initial_schema.py` | users, companies, subscriptions, prep_snapshots |
| 002 | `002_company_news.py` | company_news 테이블 |
| 003 | `003_briefing_constraints.py` | briefings unique constraint, briefing_items news_id FK |
| 004 | `004_company_job_postings.py` | company_job_postings 테이블, postingstatus enum |
| 005 | `005_prep_snapshot_constraints.py` | prep_snapshots에 generation_date, source_version 추가, unique(company_id, generation_date) |
| 006 | `006_user_password_hash.py` | users 테이블에 password_hash 컬럼 추가 (Phase 5 JWT 인증) |

```bash
# 마이그레이션 실행
alembic upgrade head

# 현재 버전 확인
alembic current

# 이전 버전으로 롤백
alembic downgrade -1

# 새 마이그레이션 생성
alembic revision --autogenerate -m "description"
```

### 테스트 데이터
```bash
# seed 스크립트 실행 (기존 데이터 삭제 후 재생성)
python -m app.scripts.seed

# 포함 내용:
# - 1명의 테스트 유저 (test@example.com / password1234)
# - 30개 기업 (대기업 10, 중견기업 10, 공공기관 10)
# - 5개 기업의 PrepSnapshot
# - 오늘 날짜의 브리핑 (6개 아이템)
# - 3개 관심기업 등록
# - 뉴스 데이터 (삼성전자 2개, 카카오 1개)
# - 채용공고 데이터 (삼성전자 2개, 카카오 1개)
```

---

## 🏗️ 프로젝트 구조

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── auth.py               # 인증 엔드포인트 (signup/login) – Phase 5
│   │   ├── users.py              # /users/me 엔드포인트 – Phase 5
│   │   ├── companies.py          # 기업 엔드포인트 (뉴스 + 채용공고 포함)
│   │   ├── subscriptions.py      # 관심기업 엔드포인트
│   │   └── briefings.py          # 브리핑 엔드포인트
│   ├── core/
│   │   ├── config.py             # 환경 설정 (Phase 1~5 설정값 포함)
│   │   ├── db.py                 # DB 연결
│   │   ├── dependencies.py       # FastAPI 의존성 (JWT get_current_user)
│   │   ├── security.py           # JWT 생성/검증 + bcrypt 해시 – Phase 5
│   │   └── response.py           # 응답 스키마
│   ├── models/
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── subscription.py
│   │   ├── prep_snapshot.py
│   │   ├── company_news.py       # Phase 1
│   │   ├── briefing.py           # Phase 2
│   │   └── company_job_posting.py # Phase 3 ← NEW
│   ├── schemas/
│   │   ├── company.py
│   │   ├── subscription.py
│   │   ├── company_news.py       # Phase 1
│   │   ├── briefing.py           # Phase 2
│   │   └── company_job_posting.py # Phase 3 ← NEW
│   ├── repositories/
│   │   ├── user_repository.py    # UserRepository – Phase 5
│   │   ├── company_repository.py
│   │   ├── subscription_repository.py
│   │   ├── company_news_repository.py  # Phase 1
│   │   ├── briefing_repository.py      # Phase 2
│   │   ├── briefing_generation_repository.py # Phase 2 배치용
│   │   └── company_job_posting_repository.py # Phase 3 ← NEW
│   ├── services/
│   │   ├── company_service.py
│   │   ├── subscription_service.py
│   │   ├── news_collection_service.py  # Phase 1
│   │   ├── briefing_service.py         # Phase 2
│   │   ├── briefing_generation_service.py # Phase 2 배치용
│   │   └── job_collection_service.py   # Phase 3 ← NEW
│   ├── domains/                  # 도메인 로직 분리
│   │   ├── auth/                 # Phase 5 ← NEW
│   │   │   ├── schemas.py        # SignupRequest, LoginRequest, TokenResponse
│   │   │   └── service.py        # AuthService (signup, authenticate, create_token)
│   │   └── prep/
│   │       ├── generator.py      # 규칙 기반 snapshot 필드 생성
│   │       ├── repository.py     # PrepSnapshot 배치 전용 DB 접근
│   │       └── service.py        # PrepSnapshotGenerationService
│   ├── scripts/
│   │   ├── seed.py
│   │   ├── news/
│   │   │   └── collect_news.py   # Phase 1 배치
│   │   ├── briefings/
│   │   │   ├── generate_today_briefings.py  # Phase 2 배치
│   │   │   └── action_point.py   # 액션 포인트 유틸
│   │   ├── jobs/                 # Phase 3
│   │   │   ├── collect_jobs.py   # 배치 스크립트
│   │   │   ├── job_posting_item.py  # DTO
│   │   │   ├── job_keywords.py   # 키워드 추출 유틸
│   │   │   ├── duplicate_key.py  # 중복 키 생성 유틸
│   │   │   └── providers/
│   │   │       ├── base.py       # 추상 Provider
│   │   │       └── saramin_provider.py  # 사람인 Provider
│   │   └── prep/                 # Phase 4 ← NEW
│   │       └── generate_prep_snapshots.py  # CLI 배치 스크립트
│   └── main.py
├── alembic/
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_company_news.py
│       ├── 003_briefing_constraints.py
│       └── 004_company_job_postings.py  # ← NEW
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

---

## 🔧 환경 변수

```bash
# ─── App ──────────────────────────────
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true

# ─── Database ─────────────────────────
DATABASE_URL=postgresql+psycopg2://jobpilot:jobpilot@localhost:5432/jobpilot
DATABASE_URL_ASYNC=postgresql+asyncpg://jobpilot:jobpilot@localhost:5432/jobpilot

# ─── Business Rules ───────────────────
SUBSCRIPTION_LIMIT=5

# ─── Phase 1: News Collection ─────────
NEWS_PROVIDER=naver
NAVER_CLIENT_ID=               # 네이버 오픈API 발급
NAVER_CLIENT_SECRET=
NEWS_DEFAULT_LIMIT=5
NEWS_LOOKBACK_DAYS=3

# ─── Phase 2: Briefing Generation ─────
BRIEFING_NEWS_LOOKBACK_DAYS=3
BRIEFING_MAX_ITEMS_PER_COMPANY=2
BRIEFING_MAX_COMPANIES_PER_USER=5

# ─── Phase 3: Job Collection ──────────
JOB_PROVIDER=saramin
SARAMIN_API_KEY=               # 사람인 오픈API 발급: https://oapi.saramin.co.kr/
JOB_DEFAULT_LIMIT=5
JOB_LOOKBACK_DAYS=30
JOB_KEYWORDS=Python,SQL,데이터,AI,금융,협업
```

`.env.example` 파일을 복사하여 실제 값을 설정하세요:
```bash
cp .env.example .env
# 각 API 키를 발급받아 .env에 입력
```

---

## 🔐 인증 (Phase 5 – JWT Bearer Token)

Phase 5부터 JWT access token 기반 실제 인증이 적용됩니다.

### 인증이 필요한 엔드포인트
- `GET /api/v1/subscriptions` – 관심기업 목록
- `POST /api/v1/subscriptions` – 관심기업 추가
- `DELETE /api/v1/subscriptions/{id}` – 관심기업 삭제
- `GET /api/v1/briefings/today` – 오늘의 브리핑
- `GET /api/v1/users/me` – 내 프로필

### 인증이 불필요한 엔드포인트 (공개)
- `GET /health`
- `GET /api/v1/companies` (목록/상세/뉴스/채용공고)
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`

### 사용 방법

```bash
# 1. 회원가입
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password1234", "nickname": "테스트유저"}'

# 2. 로그인 → access_token 저장
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")

# 3. 인증이 필요한 API 호출
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/subscriptions
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/briefings/today
```

### seed 계정
```
email:    test@example.com
password: password1234
```

### 토큰 설정
- 알고리즘: HS256
- 유효 시간: `ACCESS_TOKEN_EXPIRE_MINUTES` (기본 60분)
- SECRET_KEY: `.env`에서 설정 (운영 환경에서는 강력한 랜덤 키 사용)

```bash
# 강력한 시크릿 키 생성
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🧪 테스트 커맨드

```bash
# Health check
curl http://localhost:8000/health

# 회원가입 (신규)
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "me@example.com", "password": "password1234", "nickname": "나"}'

# 로그인
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")

# 내 프로필
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me

# 기업 목록 (공개)
curl "http://localhost:8000/api/v1/companies?limit=5"

# 기업 상세
curl "http://localhost:8000/api/v1/companies/31"

# 기업 뉴스
curl "http://localhost:8000/api/v1/companies/31/news"

# 기업 채용공고
curl "http://localhost:8000/api/v1/companies/31/jobs"

# 관심기업 목록 (인증 필요)
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/subscriptions"

# 관심기업 추가
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"company_id": 36}' \
  "http://localhost:8000/api/v1/subscriptions"

# 오늘의 브리핑
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/briefings/today"
```

---

## 📋 응답 형식

모든 API는 통일된 응답 형식을 사용합니다:

**성공 응답:**
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

**에러 응답:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지"
  }
}
```

**페이지네이션 응답:**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "limit": 20,
      "offset": 0,
      "total": 100
    }
  },
  "error": null
}
```

### GET /api/v1/companies/{id}/jobs 예시
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "삼성전자 DX부문 Software Engineer (Backend)",
        "department": "DX부문",
        "employment_type": "정규직",
        "location": "수원",
        "status": "OPEN",
        "posting_url": "https://jobs.samsung.com/...",
        "source_name": "saramin",
        "posted_at": "2026-04-10T00:00:00+00:00",
        "deadline_at": "2026-05-31T00:00:00+00:00",
        "keywords": ["Python", "백엔드", "SQL"]
      }
    ],
    "pagination": { "limit": 20, "offset": 0, "total": 2 }
  },
  "error": null
}
```

---

## 📚 API 문서

서버 실행 후 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🐳 Docker

```bash
# PostgreSQL만 실행
docker-compose up -d postgres

# 전체 서비스 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f api

# 종료
docker-compose down
```

---

## 🚦 PM2 관리

```bash
# 시작
pm2 start ecosystem.config.cjs

# 상태 확인
pm2 list

# 로그 확인
pm2 logs jobpilot-api --nostream

# 재시작
pm2 restart jobpilot-api

# 중지
pm2 stop jobpilot-api

# 삭제
pm2 delete jobpilot-api
```

---

## 🔍 트러블슈팅

### PostgreSQL 연결 실패
```bash
docker-compose ps
docker-compose logs postgres
docker-compose restart postgres
```

### Import 에러
```bash
rm -rf .venv
uv sync
```

### 마이그레이션 충돌
```bash
alembic current
alembic downgrade <revision>
alembic upgrade <revision>
```

### Saramin API 키 없을 때
```
WARNING collect_jobs – SARAMIN_API_KEY 미설정 – 수집을 건너뜁니다.
```
→ `.env`에 `SARAMIN_API_KEY=` 발급 후 설정하세요.  
→ https://oapi.saramin.co.kr/ 에서 회원가입 후 API 키 신청

---

## 📝 개발 가이드

### 새 엔드포인트 추가

1. **모델 정의** (`app/models/`)
2. **스키마 정의** (`app/schemas/`)
3. **리포지토리 작성** (`app/repositories/`)
4. **서비스 로직 작성** (`app/services/`)
5. **라우터 작성** (`app/api/v1/`)
6. **마이그레이션 생성** (`alembic revision --autogenerate`)

### 새 Job Provider 추가

```python
# app/scripts/jobs/providers/my_provider.py
from app.scripts.jobs.providers.base import BaseJobProvider
from app.scripts.jobs.job_posting_item import JobPostingItem

class MyProvider(BaseJobProvider):
    @property
    def source_name(self) -> str:
        return "my_provider"

    def fetch(self, company_name: str, limit: int = 5) -> list[JobPostingItem]:
        # 실제 API 호출 구현
        ...
```

그런 다음 `collect_jobs.py`의 `_build_provider()`에 등록합니다.

---

## 🗺️ 로드맵

| Phase | 상태 | 내용 |
|-------|------|------|
| Phase 0 | ✅ 완료 | Mock/Real API 전환 가능한 Next.js 프론트엔드 |
| Phase 1 | ✅ 완료 | 뉴스 수집 파이프라인 (Naver API) |
| Phase 2 | ✅ 완료 | 브리핑 자동 생성 배치 |
| Phase 3 | ✅ 완료 | 채용공고 수집 파이프라인 (Saramin API) |
| Phase 4 | ✅ 완료 | PrepSnapshot 자동 생성 배치 (rule-based, daily 정책) |
| Phase 5 | ✅ 완료 | JWT access token 인증 (signup/login/users/me) |
| Phase 6 | 🔜 예정 | 이메일/알림 발송 (SendGrid, Firebase) |
| Phase 7 | 🔜 예정 | 채용공고 데이터 → 브리핑 통합 (BriefingItem source_type='job') |

---

**Last Updated:** 2026-04-15
