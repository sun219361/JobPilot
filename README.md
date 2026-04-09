# JobPilot - 취업 준비생을 위한 관심기업 브리핑 서비스 (Phase 0)

## 📋 프로젝트 개요

취업 준비생이 관심기업을 등록하고, 해당 기업의 뉴스와 채용 공고를 매일 브리핑으로 받아볼 수 있는 서비스입니다.

**현재 구현 범위 (Phase 0):**
- ✅ 관심기업 등록/삭제 (최대 5개)
- ✅ 기업 검색 및 상세 정보 조회
- ✅ 기업별 채용 준비 스냅샷 제공
- ✅ 오늘의 브리핑 조회
- ✅ Mock/Real API 전환 가능한 클라이언트 구조

**제외된 기능 (향후 Phase):**
- ❌ 뉴스/채용 공고 자동 수집
- ❌ 이메일/카카오톡 알림
- ❌ 관리자 기능
- ❌ 인증/인가 (JWT는 구조만 준비)
- ❌ Redis 캐싱, OpenAI 통합

## 🏗️ 프로젝트 구조

```
webapp/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── api/v1/            # API 라우터 (companies, subscriptions, briefings)
│   │   ├── core/              # 설정, DB, 의존성, 응답 스키마
│   │   ├── models/            # SQLAlchemy 모델
│   │   ├── schemas/           # Pydantic 스키마
│   │   ├── repositories/      # DB 접근 계층
│   │   ├── services/          # 비즈니스 로직
│   │   ├── scripts/           # seed.py (테스트 데이터 생성)
│   │   └── main.py            # FastAPI 앱 진입점
│   ├── alembic/               # DB 마이그레이션
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
└── frontend/                   # Next.js 14 App Router
    ├── app/
    │   ├── page.tsx           # 랜딩 페이지
    │   ├── subscriptions/     # 관심기업 관리
    │   ├── companies/[id]/    # 기업 상세 정보
    │   └── briefings/today/   # 오늘의 브리핑
    ├── components/
    │   ├── common/            # 공통 컴포넌트 (Header, Skeleton, Empty, Error)
    │   ├── subscriptions/     # 관심기업 관련 컴포넌트
    │   ├── companies/         # 기업 상세 관련 컴포넌트
    │   └── briefings/         # 브리핑 관련 컴포넌트
    ├── lib/
    │   ├── api/               # API 클라이언트 (config, http, clients)
    │   │   └── mock/          # Mock 클라이언트 구현
    │   ├── types/             # TypeScript 타입 정의
    │   ├── mock/              # Mock 데이터
    │   └── utils/             # 유틸리티 함수
    └── .env.example
```

## 🚀 빠른 시작

### 1. 백엔드 실행

```bash
cd backend

# PostgreSQL 시작 (Docker 사용)
docker-compose up -d postgres

# 의존성 설치 (uv 사용)
uv sync

# 환경변수 설정
cp .env.example .env

# DB 마이그레이션
alembic upgrade head

# 테스트 데이터 생성
python -m app.scripts.seed

# 개발 서버 시작 (PM2)
pm2 start ecosystem.config.cjs

# 또는 직접 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**백엔드 API 문서:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 프론트엔드 실행

```bash
cd frontend

# 의존성 설치
npm install

# 환경변수 설정 (Mock 모드)
cp .env.example .env.local
# NEXT_PUBLIC_USE_MOCK=true

# 개발 서버 시작
npm run dev

# 또는 프로덕션 빌드
npm run build
pm2 start ecosystem.config.cjs
```

**프론트엔드 URL:**
- Local: http://localhost:3000
- Public (Sandbox): https://3000-ix2krp6d80cvydxsp6ch8-b9b802c4.sandbox.novita.ai

### 3. Mock/Real API 전환

**Mock 모드 (백엔드 불필요):**
```bash
# frontend/.env.local
NEXT_PUBLIC_USE_MOCK=true
```

**Real API 모드 (백엔드 필요):**
```bash
# frontend/.env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=false
```

환경변수 변경 후 프론트엔드를 재빌드해야 합니다:
```bash
cd frontend
npm run build
pm2 restart jobpilot-frontend
```

## 📡 API 엔드포인트

### Health Check
- `GET /health` - 서버 상태 확인

### Companies (기업)
- `GET /api/v1/companies` - 기업 목록 조회
  - Query: `q` (검색), `company_type` (LARGE/MID/PUBLIC), `limit`, `offset`
- `GET /api/v1/companies/{id}` - 기업 상세 조회 (최신 prep_snapshot 포함)

### Subscriptions (관심기업)
- `GET /api/v1/subscriptions` - 현재 사용자의 관심기업 목록
- `POST /api/v1/subscriptions` - 관심기업 추가
  - Body: `{"company_id": 1, "memo": "메모"}`
- `DELETE /api/v1/subscriptions/{id}` - 관심기업 삭제

### Briefings (브리핑)
- `GET /api/v1/briefings/today` - 오늘의 브리핑 조회

## 💾 데이터 모델

### Company (기업)
- 기업 유형: LARGE (대기업), MID (중견기업), PUBLIC (공공기관)
- 산업 분류, 요약 정보, 홈페이지/채용 URL

### PrepSnapshot (채용 준비 스냅샷)
- 한 줄 요약, 최근 이슈, 채용 동향, 인재상
- 자소서 포인트, 면접 포인트 (리스트)
- 생성 일시

### Subscription (관심기업)
- 사용자 - 기업 매핑 (최대 5개)
- unique constraint on (user_id, company_id)

### Briefing (브리핑)
- 날짜별 브리핑 제목
- 여러 BriefingItem으로 구성

### BriefingItem (브리핑 아이템)
- 뉴스/채용공고 구분 (source_type)
- 헤드라인, 요약, 액션 포인트
- 정렬 순서 (sort_order)

## 🔐 인증 (준비 단계)

현재는 fake current user (id=1)를 사용합니다.

**JWT 전환 방법:**
```python
# backend/app/core/dependencies.py
# get_current_user 함수만 수정하면 전체 라우터에 JWT 인증 적용됨

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # JWT 토큰 검증 로직
    ...
```

## 🧪 테스트

### 백엔드 API 테스트
```bash
# Health check
curl http://localhost:8000/health

# 기업 목록
curl "http://localhost:8000/api/v1/companies?limit=5"

# 기업 검색
curl --get --data-urlencode "q=삼성" "http://localhost:8000/api/v1/companies"

# 기업 상세
curl "http://localhost:8000/api/v1/companies/31"

# 관심기업 목록
curl "http://localhost:8000/api/v1/subscriptions"

# 관심기업 추가
curl -X POST "http://localhost:8000/api/v1/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{"company_id": 36}'

# 오늘의 브리핑
curl "http://localhost:8000/api/v1/briefings/today"
```

## 🎨 기술 스택

### Backend
- **Framework:** FastAPI 0.115+
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.x
- **Migration:** Alembic
- **Validation:** Pydantic v2
- **Package Manager:** uv (or poetry)

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State:** React State + Context (simple)
- **Data Fetching:** Custom fetch wrapper (no React Query/SWR)

## 📝 개발 원칙

1. **실행 가능한 코드 우선** - 추상화보다 동작하는 코드
2. **도메인 중심 구조** - 복잡도는 최소화
3. **일관된 응답 형식** - `{success, data, error}` 구조
4. **간단한 상태 관리** - loading, success, empty, error
5. **Mock/Real 전환 가능** - 개발/테스트 편의성

## 🔄 다음 단계 (Phase 1+)

- [ ] JWT 인증/인가 구현
- [ ] 뉴스/채용공고 자동 수집 (크롤링/API)
- [ ] 이메일/카카오톡 알림 발송
- [ ] 관리자 페이지 (기업 관리, 브리핑 생성)
- [ ] Redis 캐싱 적용
- [ ] OpenAI API 통합 (요약 생성)
- [ ] 배포 환경 구성 (AWS/GCP)

## 📄 라이선스

MIT

## 👥 기여자

- Backend: FastAPI + PostgreSQL + SQLAlchemy 2.x
- Frontend: Next.js 14 App Router + TypeScript + Tailwind CSS

---

**Last Updated:** 2026-04-09
**Version:** Phase 0 (MVP)
