# 관심기업 브리핑 서비스 — MVP 설계 문서 v4 (최종)

> **목표**: 실사용자 30명 확보를 위한 초기 출시
> **원칙**: 동작하는 서비스를 가장 빠르게, 가장 단순하게
> **버전**: v4 (코드 생성 직전 최종본)

---

## 변경 이유 요약 (v3 → v4)

| # | 수정 항목 | 변경 이유 |
|---|-----------|-----------|
| 1 | prep 도메인 / companies API 경계 | 내부는 독립 도메인 유지, 외부 응답에서는 companies/{id}에 latest prep snapshot 포함 → 프론트 API 호출 수 감소 |
| 2 | MVP 응답 필드 최소화 | null 필드를 내려주면 프론트가 null 체크 로직을 만들어야 한다. 존재하지 않는 필드는 응답에서 완전히 제거하고 문서에만 명시 |
| 3 | 공기업 수집 fallback 전략 | 공공데이터포털 API 커버리지가 전체 공기업을 포함하지 않는다. fallback 없이 단일 소스 의존 시 수집 공백이 생긴다 |
| 4 | 로드맵 더미 데이터 일관성 | 상단 원칙에 "더미 우선" 이 있었지만 실제 Phase 본문에 반영되지 않았다. 배치 자동화 전에도 핵심 화면을 보여주는 흐름으로 통일 |

---

## 0. MVP 핵심 가치 재확인

```
사용자가 얻는 것:
  "내가 지원할 기업을 저장해두면,
   매일 아침 그 기업의 최신 소식을 요약해서 보여주고,
   기업별 자소서/면접 준비 포인트를 제공한다."

핵심 3기능:
  ① 관심기업 등록   → 내가 준비할 기업을 고른다
  ② 오늘의 브리핑   → 매일 아침 기업별 최신 소식이 쌓인다
  ③ 기업 준비 카드  → 뉴스 + 채용공고 기반 준비 가이드

개발 원칙:
  더미 데이터로 화면을 먼저 완성한다.
  사용자가 화면을 보고 피드백을 주면 배치 자동화를 붙인다.
  없는 기능은 null로 내려주지 않는다. 아예 없는 필드처럼 다룬다.
```

---

## 1. 전체 아키텍처

```
┌──────────────────────────────────────────────────────┐
│                    CLIENT LAYER                       │
│         Next.js (TypeScript + Tailwind CSS)           │
│                                                       │
│  /login   /dashboard   /briefing   /company/:id       │
└──────────────────────┬───────────────────────────────┘
                       │ REST API (HTTPS)
┌──────────────────────▼───────────────────────────────┐
│                    API LAYER                          │
│              FastAPI  /api/v1/...                     │
│                                                       │
│   auth │ users │ companies │ subscriptions │ briefings│
│                                                       │
│   [내부 도메인: prep]  ← companies/{id} 응답에 포함    │
└──────────┬──────────────────────────┬────────────────┘
           │                          │
┌──────────▼──────────┐   ┌──────────▼──────────────┐
│    DATA LAYER        │   │     BATCH LAYER          │
│    PostgreSQL         │   │  Python Script + Cron    │
│                      │   │                          │
│  - users             │   │  매일 06:00               │
│  - companies         │   │  ① 뉴스 수집              │
│  - subscriptions     │◀──│  ② 채용공고 수집           │
│  - news_articles     │   │  ③ 브리핑 생성             │
│  - job_postings      │   │  ④ prep 스냅샷 갱신        │
│  - briefings         │   │                          │
│  - briefing_items    │   │  [외부 소스]               │
│  - prep_snapshots    │   │  - 네이버 뉴스 API         │
└──────────────────────┘   │  - 공공데이터포털 API      │
                           │  - 사람인 API (fallback)  │
                           └──────────────────────────┘
```

---

## 2. 도메인 구조

### 핵심 도메인 (5개 공개 API)

```
auth          → 로그인 / 회원가입 / JWT 발급
users         → 내 계정 조회/수정
companies     → 기업 목록/상세 (+ prep snapshot 포함 응답)
subscriptions → 관심기업 등록/해제/목록
briefings     → 브리핑 조회
```

### prep 도메인 위치 결정

```
[내부 구조]  독립 도메인 유지
  domains/prep/
    ├── router.py       ← GET /prep/:company_id (독립 엔드포인트 유지)
    ├── service.py
    ├── repository.py
    ├── model.py
    └── schema.py

[외부 API 응답]  companies/{id}에 최신 스냅샷 포함
  GET /companies/{id}
    └── "prep_snapshot": { ... }  ← prep.repository를 companies.service가 호출

이유:
  - 프론트엔드가 기업 상세 페이지 렌더링에 필요한 모든 정보를 1회 API 호출로 획득
  - prep 도메인 내부 로직(생성/이력관리)은 companies와 완전히 분리 유지
  - GET /prep/:company_id 엔드포인트는 독립 유지 (향후 준비 메모/진도 기능 확장 대비)
```

### 폴더 구조

```
backend/
├── app/
│   ├── main.py
│   ├── config.py               # Settings (SUBSCRIPTION_LIMIT 등)
│   ├── database.py
│   ├── dependencies.py         # get_db, get_current_user
│   │
│   ├── domains/
│   │   ├── auth/
│   │   │   ├── router.py       # POST /auth/register, /auth/login
│   │   │   ├── service.py
│   │   │   ├── schema.py
│   │   │   └── utils.py        # JWT 생성/검증, bcrypt
│   │   │
│   │   ├── users/
│   │   │   ├── router.py       # GET/PATCH/DELETE /users/me
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── model.py
│   │   │   └── schema.py
│   │   │
│   │   ├── companies/
│   │   │   ├── router.py       # GET /companies, GET /companies/{id}
│   │   │   ├── service.py      # prep.repository 호출하여 snapshot 포함
│   │   │   ├── repository.py
│   │   │   ├── model.py        # Company, NewsArticle, JobPosting
│   │   │   └── schema.py       # CompanyDetailResponse (prep_snapshot 포함)
│   │   │
│   │   ├── subscriptions/
│   │   │   ├── router.py       # GET/POST/DELETE /subscriptions
│   │   │   ├── service.py      # SUBSCRIPTION_LIMIT 정책 적용
│   │   │   ├── repository.py
│   │   │   ├── model.py
│   │   │   └── schema.py
│   │   │
│   │   ├── briefings/
│   │   │   ├── router.py       # GET /briefings, /briefings/today, /briefings/{id}
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── model.py        # Briefing, BriefingItem
│   │   │   └── schema.py
│   │   │
│   │   └── prep/               # 내부 독립 도메인
│   │       ├── router.py       # GET /prep/{company_id}
│   │       ├── service.py
│   │       ├── repository.py   # companies.service에서도 참조
│   │       ├── model.py        # PrepSnapshot
│   │       └── schema.py       # PrepSnapshotResponse
│   │
│   └── core/
│       ├── exceptions.py       # AppException, SubscriptionLimitExceeded
│       ├── error_handlers.py
│       └── pagination.py
│
├── batch/
│   ├── run.py                  # 배치 진입점
│   ├── tasks/
│   │   ├── collect_news.py
│   │   ├── collect_jobs.py
│   │   ├── generate_briefing.py
│   │   └── generate_prep.py
│   └── sources/
│       ├── base.py             # BaseCollector (추상)
│       ├── large_corp.py       # 대기업 수집기
│       ├── mid_corp.py         # 중견기업 수집기
│       └── public_corp.py      # 공기업 수집기 (fallback 포함)
│
├── alembic/
│   └── versions/
│       └── 001_initial_schema.py
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_subscriptions.py
│   └── test_briefings.py
│
├── seeds/
│   ├── companies.sql           # 초기 기업 시드 데이터 (50개)
│   └── prep_snapshots.sql      # 초기 prep 더미 데이터 (대기업 5개)
│
├── .env.example
├── requirements.txt
├── alembic.ini
└── docker-compose.yml          # PostgreSQL 단독
```

---

## 3. DB 테이블 설계

### users
```sql
CREATE TABLE users (
  id              SERIAL PRIMARY KEY,
  email           VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  name            VARCHAR(100) NOT NULL,
  is_active       BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### companies
```sql
CREATE TABLE companies (
  id          SERIAL PRIMARY KEY,
  name        VARCHAR(200) UNIQUE NOT NULL,
  slug        VARCHAR(200) UNIQUE NOT NULL,   -- 'samsung-electronics'
  category    VARCHAR(20)  NOT NULL,           -- 'large' | 'mid' | 'public'
  industry    VARCHAR(100),                    -- 'IT/전자', '금융', '에너지'
  logo_url    TEXT,
  description TEXT,
  website_url TEXT,
  press_url   TEXT,                            -- 공기업 보도자료 페이지 URL
  is_active   BOOLEAN DEFAULT TRUE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### subscriptions
```sql
CREATE TABLE subscriptions (
  id         SERIAL PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (user_id, company_id)
);
```

### news_articles
```sql
CREATE TABLE news_articles (
  id           SERIAL PRIMARY KEY,
  company_id   INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  title        VARCHAR(500) NOT NULL,
  summary      TEXT,                      -- 본문 excerpt (200자 내외)
  source_url   TEXT UNIQUE NOT NULL,
  source_name  VARCHAR(100),              -- '네이버뉴스', '조선비즈' 등
  published_at TIMESTAMPTZ,
  collected_at TIMESTAMPTZ DEFAULT NOW()
);
```

### job_postings
```sql
CREATE TABLE job_postings (
  id           SERIAL PRIMARY KEY,
  company_id   INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  title        VARCHAR(500) NOT NULL,
  job_type     VARCHAR(30),               -- 'full_time' | 'internship' | 'contract'
  location     VARCHAR(100),
  source_url   TEXT UNIQUE NOT NULL,
  source_name  VARCHAR(100),              -- '사람인', '공공데이터포털', '공식사이트'
  posted_at    TIMESTAMPTZ,
  deadline_at  TIMESTAMPTZ,
  is_active    BOOLEAN DEFAULT TRUE,
  collected_at TIMESTAMPTZ DEFAULT NOW()
);
```

### briefings
```sql
CREATE TABLE briefings (
  id            SERIAL PRIMARY KEY,
  user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  briefing_date DATE NOT NULL,
  is_read       BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (user_id, briefing_date)
);
```

### briefing_items
```sql
CREATE TABLE briefing_items (
  id          SERIAL PRIMARY KEY,
  briefing_id INTEGER NOT NULL REFERENCES briefings(id) ON DELETE CASCADE,
  company_id  INTEGER NOT NULL REFERENCES companies(id),
  item_type   VARCHAR(20) NOT NULL,        -- 'news' | 'job'
  -- 명시적 FK (둘 중 하나만 채워짐, 다형 참조 제거)
  news_id     INTEGER REFERENCES news_articles(id) ON DELETE SET NULL,
  job_id      INTEGER REFERENCES job_postings(id)  ON DELETE SET NULL,
  -- 브리핑 시점 복사본 (원본 삭제 후에도 브리핑 내용 유지)
  title       VARCHAR(500) NOT NULL,
  summary     TEXT,
  source_url  TEXT,
  display_order SMALLINT DEFAULT 0,
  created_at  TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT chk_item_ref CHECK (
    (item_type = 'news' AND news_id IS NOT NULL AND job_id IS NULL) OR
    (item_type = 'job'  AND job_id  IS NOT NULL AND news_id IS NULL)
  )
);
```

### prep_snapshots
```sql
CREATE TABLE prep_snapshots (
  id                  SERIAL PRIMARY KEY,
  company_id          INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  snapshot_date       DATE NOT NULL,
  talent_profile      TEXT,               -- 인재상 요약 (채용공고 + description 기반)
  recent_news_summary TEXT,               -- 최근 7일 뉴스 요약
  job_trend_summary   TEXT,               -- 현재 채용 흐름 요약
  resume_points       JSONB,              -- [{ "point": "...", "source": "..." }]
  interview_points    JSONB,              -- [{ "point": "...", "source": "..." }]
  data_sources        JSONB,              -- ["news_articles", "job_postings", ...]
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (company_id, snapshot_date)
);
```

### 인덱스
```sql
CREATE INDEX idx_sub_user      ON subscriptions(user_id);
CREATE INDEX idx_sub_company   ON subscriptions(company_id);
CREATE INDEX idx_news_company  ON news_articles(company_id);
CREATE INDEX idx_news_pub      ON news_articles(company_id, published_at DESC);
CREATE INDEX idx_job_company   ON job_postings(company_id);
CREATE INDEX idx_job_active    ON job_postings(company_id, is_active, deadline_at);
CREATE INDEX idx_brief_user    ON briefings(user_id);
CREATE INDEX idx_brief_date    ON briefings(user_id, briefing_date DESC);
CREATE INDEX idx_bitem_brief   ON briefing_items(briefing_id);
CREATE INDEX idx_bitem_co      ON briefing_items(company_id);
CREATE INDEX idx_prep_co_date  ON prep_snapshots(company_id, snapshot_date DESC);
CREATE INDEX idx_co_category   ON companies(category);
-- 한글 검색: pg_trgm 익스텐션 활성화 후
CREATE INDEX idx_co_name_trgm  ON companies USING gin (name gin_trgm_ops);
```

---

## 4. API 명세 (MVP 최소화 버전)

> Base URL: `/api/v1`
> 인증: `Authorization: Bearer <access_token>`
> **원칙**: MVP에서 존재하지 않는 기능은 응답 필드 자체를 포함하지 않는다

---

### 🔐 Auth

| Method | Path | 설명 | Auth |
|--------|------|------|:----:|
| POST | `/auth/register` | 회원가입 + Access Token 반환 | ❌ |
| POST | `/auth/login` | 로그인 + Access Token 반환 | ❌ |

```
Access Token 만료: 7일 (MVP)
Refresh Token: Phase 4에서 도입
```

```json
// POST /auth/login
// Request
{ "email": "user@example.com", "password": "..." }

// Response 200
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": 1, "email": "user@example.com", "name": "홍길동" }
}
```

---

### 👤 Users

| Method | Path | 설명 | Auth |
|--------|------|------|:----:|
| GET | `/users/me` | 내 프로필 | ✅ |
| PATCH | `/users/me` | 이름 수정 | ✅ |
| DELETE | `/users/me` | 회원 탈퇴 | ✅ |

```json
// GET /users/me Response
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "subscription_count": 3,
  "subscription_limit": 5,     // settings.SUBSCRIPTION_LIMIT 값 노출
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### 🏢 Companies

| Method | Path | 설명 | Auth |
|--------|------|------|:----:|
| GET | `/companies` | 기업 목록 | ✅ |
| GET | `/companies/{id}` | 기업 상세 + latest prep snapshot | ✅ |

```
GET /companies?q=삼성&category=large&industry=IT&page=1&size=20
category: large | mid | public
```

```json
// GET /companies/{id} Response
// ─── companies.service가 prep.repository.get_latest()를 호출하여 조합 ───
{
  "id": 1,
  "name": "삼성전자",
  "slug": "samsung-electronics",
  "category": "large",
  "industry": "IT/전자",
  "logo_url": "...",
  "description": "...",
  "website_url": "https://samsung.com",
  "is_subscribed": true,
  "stats": {
    "latest_news_count": 5,
    "active_job_count": 2
  },
  // prep_snapshot: 최신 스냅샷이 있으면 포함, 없으면 필드 자체 생략
  "prep_snapshot": {
    "snapshot_date": "2024-01-15",
    "talent_profile": "글로벌 기술 리더십과 창의적 문제해결 강조...",
    "recent_news_summary": "HBM4 양산, 파운드리 수주 확대...",
    "job_trend_summary": "DS부문 중심 채용 확대. 소프트웨어 직군 비중 증가.",
    "resume_points": [
      { "point": "직무 연계 경험을 수치로 제시", "source": "채용공고 직무 기술서" }
    ],
    "interview_points": [
      { "point": "지원 직무의 최근 사업 방향과 연계한 답변 준비", "source": "최근 뉴스 및 채용공고" }
    ],
    "data_sources": ["news_articles", "job_postings", "company_description"]
  }
  // prep_snapshot이 없을 때: 필드 자체 없음 (null 아님)
  // 프론트: if (company.prep_snapshot) { ... } 단일 체크만 필요
}
```

**내부 구조와 외부 응답 분리 흐름:**
```
[요청]  GET /companies/1
  └─▶ companies.router
        └─▶ companies.service.get_company_detail(id, current_user)
              ├─▶ companies.repository.get_by_id(id)        → Company
              ├─▶ prep.repository.get_latest(company_id)    → PrepSnapshot | None
              └─▶ CompanyDetailResponse 조합하여 반환
                    (prep_snapshot 없으면 해당 키 제외)
```

---

### ⭐ Subscriptions

| Method | Path | 설명 | Auth |
|--------|------|------|:----:|
| GET | `/subscriptions` | 내 관심기업 목록 | ✅ |
| POST | `/subscriptions` | 관심기업 등록 | ✅ |
| DELETE | `/subscriptions/{company_id}` | 관심기업 해제 | ✅ |

```json
// POST /subscriptions
// Request
{ "company_id": 1 }

// Response 201
{
  "id": 10,
  "company": { "id": 1, "name": "삼성전자", "category": "large", "logo_url": "..." },
  "created_at": "2024-01-15T09:00:00Z"
}

// 한도 초과 에러 Response 422
{
  "error": {
    "code": "SUBSCRIPTION_LIMIT_EXCEEDED",
    "message": "관심기업은 최대 5개까지 등록할 수 있습니다.",
    "limit": 5,
    "current": 5
  }
}
```

```json
// GET /subscriptions Response
{
  "items": [
    {
      "id": 10,
      "company": { "id": 1, "name": "삼성전자", "category": "large", "logo_url": "..." },
      "created_at": "..."
    }
  ],
  "total": 3,
  "limit": 5   // 현재 적용 한도 포함 → 프론트 "3/5 사용 중" UI 가능
}
```

---

### 📰 Briefings

| Method | Path | 설명 | Auth |
|--------|------|------|:----:|
| GET | `/briefings` | 내 브리핑 목록 (최근 30일) | ✅ |
| GET | `/briefings/today` | 오늘 브리핑 | ✅ |
| GET | `/briefings/{id}` | 특정 브리핑 상세 | ✅ |
| PATCH | `/briefings/{id}/read` | 읽음 처리 | ✅ |

```json
// GET /briefings/today Response — 브리핑 있을 때
{
  "id": 100,
  "briefing_date": "2024-01-15",
  "is_read": false,
  "summary": {
    "total_items": 7,
    "news_count": 5,
    "job_count": 2,
    "companies_covered": 3
  },
  "items_by_company": [
    {
      "company": { "id": 1, "name": "삼성전자", "logo_url": "..." },
      "items": [
        {
          "id": 201,
          "item_type": "news",
          "title": "삼성전자, 2024 HBM4 양산 개시 발표",
          "summary": "삼성전자가 4분기 내 HBM4 양산을 시작한다고...",
          "source_url": "https://...",
          "display_order": 1
        }
      ]
    }
  ]
}

// GET /briefings/today Response — 브리핑 없을 때
// (null 대신 명확한 상태 표현)
{
  "exists": false,
  "reason": "no_subscription",   // "no_subscription" | "pending_batch"
  "message": "관심기업을 등록하면 내일 아침 첫 브리핑이 시작됩니다."
}
```

---

### 📋 Prep (독립 엔드포인트 유지)

| Method | Path | 설명 | Auth |
|--------|------|------|:----:|
| GET | `/prep/{company_id}` | 기업 준비 카드 최신 스냅샷 | ✅ |

```json
// GET /prep/{company_id} Response — 스냅샷 있을 때
{
  "company": { "id": 1, "name": "삼성전자", "logo_url": "..." },
  "snapshot_date": "2024-01-15",
  "talent_profile": "글로벌 기술 리더십과 창의적 문제해결 강조...",
  "recent_news_summary": "HBM4 양산 일정 발표, 파운드리 수주 확대...",
  "job_trend_summary": "DS부문 중심 채용 확대. 소프트웨어 직군 비중 증가.",
  "resume_points": [
    { "point": "직무 연계 프로젝트 경험을 수치로 제시", "source": "채용공고 직무 기술서" },
    { "point": "AI·반도체 관련 역량 키워드 활용 권장", "source": "채용공고 우대사항 분석" }
  ],
  "interview_points": [
    { "point": "지원 직무의 최근 사업 방향 숙지", "source": "최근 뉴스 및 채용공고" },
    { "point": "공식 채용사이트 직무 소개 섹션 정독 권장", "source": "공식 채용사이트" }
  ],
  "data_sources": ["news_articles", "job_postings", "company_description"],
  "generated_at": "2024-01-15T06:30:00Z"
}

// 스냅샷 없을 때
{
  "company": { "id": 1, "name": "삼성전자" },
  "exists": false,
  "message": "준비 카드는 매일 새벽 업데이트됩니다."
}

// ── 후속 필드 (Phase 2+ 이후 추가 예정, MVP 응답에 포함하지 않음) ──
// exam_analysis    : 필기시험 유형 분석 (공기업 NCS, 대기업 GSAT 등)
// review_summary   : 면접 후기 기반 분석
// competitor_insight: 경쟁사 비교 분석
```

> **MVP 응답 필드 최소화 원칙**
> - `exam_analysis`, `review_summary` 등 Phase 2 이후 기능은 응답 JSON에 포함하지 않는다
> - null로 내려주면 프론트가 `if (data.exam_analysis !== null)` 같은 null 체크를 구현해야 한다
> - 필드 자체를 제거하면 `if (data.exam_analysis)` 조차 불필요하다
> - 추가될 필드는 이 문서의 "후속 필드" 섹션에만 명시한다

---

### 공통 에러 응답

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자 친화적 메시지"
  }
}
```

| HTTP | Code | 발생 상황 |
|------|------|----------|
| 400 | `VALIDATION_ERROR` | 입력값 오류 |
| 401 | `UNAUTHORIZED` | 토큰 없음 |
| 401 | `TOKEN_EXPIRED` | 토큰 만료 (7일) |
| 404 | `NOT_FOUND` | 리소스 없음 |
| 409 | `DUPLICATE_SUBSCRIPTION` | 중복 구독 |
| 422 | `SUBSCRIPTION_LIMIT_EXCEEDED` | 구독 한도 초과 (limit, current 포함) |
| 500 | `INTERNAL_ERROR` | 서버 오류 |

---

## 5. 관심기업 한도 정책

```python
# app/config.py
class Settings(BaseSettings):
    # MVP 기본값: 5개
    # 근거: 3개 → 대/중/공 각 1개씩이면 탐색 불가
    #        10개 → 브리핑 품질보다 양이 앞서면 핵심 가치 희석
    #         5개 → "진지한 준비 기업 수"로 현실적, 유료 플랜 기준점
    SUBSCRIPTION_LIMIT: int = 5

    class Config:
        env_file = ".env"
```

```bash
# .env.example
SUBSCRIPTION_LIMIT=5

# Phase 4 유료 플랜 도입 시
# SUBSCRIPTION_LIMIT_FREE=5
# SUBSCRIPTION_LIMIT_PRO=20
```

```python
# core/exceptions.py
class SubscriptionLimitExceeded(AppException):
    def __init__(self, limit: int, current: int):
        super().__init__(
            code="SUBSCRIPTION_LIMIT_EXCEEDED",
            message=f"관심기업은 최대 {limit}개까지 등록할 수 있습니다.",
            http_status=422,
            extra={"limit": limit, "current": current}
        )
```

---

## 6. 배치 구조

```
cron: 0 6 * * *  →  python batch/run.py

실행 순서:
  Step 1. collect_news.py       → 구독 기업 뉴스 수집
  Step 2. collect_jobs.py       → 구독 기업 채용공고 수집
  Step 3. generate_briefing.py  → 유저별 오늘 브리핑 생성
  Step 4. generate_prep.py      → 기업별 준비 카드 스냅샷 갱신

오류 처리:
  - 특정 기업 수집 실패 → 해당 기업 건너뛰고 계속 진행
  - 특정 유저 브리핑 실패 → 해당 유저 건너뛰고 계속 진행
  - 모든 실패는 batch/logs/YYYY-MM-DD.log에 기록
  - MVP에서는 알림 없이 로그만
```

---

## 7. 수집 전략

### 대기업 (category = 'large')

```
뉴스 수집:
  - 네이버 뉴스 검색 API: "{기업명}" 키워드
  - 출처 필터: 경제지 우선 (한국경제, 매일경제, 조선비즈)
  - 중복 제목 유사도 85% 이상 제거
  - 수집 범위: 최근 24시간, 최대 5건

채용공고 수집:
  - 1순위: 공식 채용사이트 RSS/API (기업별 URL 목록 관리)
  - 2순위: 사람인 API (공식 사이트 장애 시 fallback)

준비 카드 재료:
  - 채용공고 "지원자격/우대사항" 텍스트 기반
  - companies.description + 채용공고 텍스트 기반 인재상 요약
```

### 중견기업 (category = 'mid')

```
뉴스 수집:
  - 네이버 뉴스 검색 API: "{기업명}" + "{기업명} 채용"
  - 결과 3건 미만이면 스킵 (노이즈 방지)

채용공고 수집:
  - 1순위: 사람인 API (기업명 검색)
  - 2순위: 잡코리아 API
  - 공식 채용페이지 있는 기업은 URL 별도 등록 관리

준비 카드 재료:
  - 채용공고 텍스트 기반
  - 인재상 없으면 "채용공고 기반 추정" 명시
```

### 공기업 (category = 'public')

```
뉴스 수집:
  - 네이버 뉴스 검색 API: "{기관명}" + "{기관명} 사업/정책"
  - press_url 있는 기관은 보도자료 페이지 추가 수집

채용공고 수집:  (아래 표 참조)

준비 카드 재료:
  - 채용공고 "직무소개/지원자격" 텍스트 기반
  - 공식 채용공고 원문 URL 직접 링크 제공
```

---

## 8. 공기업 채용공고 수집 Fallback 전략

### 수집 우선순위 및 예외 케이스

| 순위 | 소스 | 커버리지 | 장점 | 한계 | 사용 조건 |
|------|------|----------|------|------|-----------|
| **1** | **공공데이터포털 채용공고 API** | 중앙부처 산하 공공기관 중심 | 구조화된 데이터, 공식 출처 | 소규모 지방공기업 누락 가능, API 응답 지연 | 항상 1순위 시도 |
| **2** | **기관 공식 채용페이지** | 개별 기관 100% | 정확도 최고, 원문 직접 | 기관마다 URL/구조 다름, 파싱 유지보수 필요 | 공공데이터 미커버 기관 |
| **3** | **사람인 API** | 공기업 포함 다수 | 구조 통일, API 안정적 | 공고 등록 시점 지연, 일부 공고 누락 | 1+2 모두 실패 시 |
| **4** | **수동 등록** | 100% (운영자 직접) | 정확도 보장 | 운영 부담 | 주요 공기업 초기 시드 |

### 예외 케이스 처리

| 케이스 | 처리 방식 |
|--------|-----------|
| 공공데이터 API 응답 없음 (타임아웃) | 기관 공식 채용페이지 → 사람인 순으로 fallback |
| 기관 공식 채용페이지 구조 변경으로 파싱 실패 | 사람인 API fallback + 파싱 오류 로그 기록 |
| 공공데이터 API에 기관 자체가 미등록 | companies 테이블의 website_url + "/recruit" 경로 시도 |
| 모든 소스 수집 실패 | 해당 기업 스킵, 로그에 "수집 실패 기관" 기록 |
| 마감일이 지난 공고 재수집 | is_active = FALSE 처리 (삭제 아님) |

### 수집기 선택 로직

```python
# batch/sources/public_corp.py

class PublicCorpCollector(BaseCollector):
    def collect_jobs(self, company: Company) -> list[JobPostingCreate]:
        results = []

        # 1순위: 공공데이터포털 API
        results = self._try_public_data_api(company)
        if results:
            return results

        # 2순위: 기관 공식 채용페이지 (URL 등록된 경우만)
        if company.website_url:
            results = self._try_official_site(company)
        if results:
            return results

        # 3순위: 사람인 API fallback
        results = self._try_saramin_api(company)
        if results:
            return results

        # 모두 실패
        logger.warning(f"[공기업 수집 실패] company_id={company.id}, name={company.name}")
        return []
```

### MVP 커버리지 목표

```
MVP 초기 공기업 대상: 20개 기관 선정
  - 한국전력공사, 한국수자원공사, 한국철도공사(코레일)
  - 한국가스공사, 한국토지주택공사(LH), 국민건강보험공단
  - 국민연금공단, 한국도로공사, 인천국제공항공사
  - 한국수력원자력 등 취준생 선호도 높은 기관 우선

수집 검증 기준:
  - 배치 실행 후 최소 1건 이상 수집: 정상
  - 연속 3일 수집 0건: 수집 오류 의심 → 로그 확인 필요
```

---

## 9. 개발 로드맵 (최종)

### 핵심 원칙

```
원칙 1: 더미 데이터로 화면을 먼저 완성한다
  배치 자동화 전에 사용자가 핵심 가치를 체감하게 한다.
  화면이 먼저 있어야 피드백도 빠르고 개발 방향도 검증된다.

원칙 2: 실제 배치는 화면 완성 후 붙인다
  배치 자동화는 "화면이 완성된 상태에서 데이터를 채우는 작업"이다.

원칙 3: 없는 기능은 보여주지 않는다
  Phase 2 기능은 화면에 없다. null 상태 UI도 없다.
```

---

### Phase 0 — 환경 설정 (Day 1~2)

```
목표: 개발 환경 최소 세팅

□ docker-compose.yml (PostgreSQL 단독)
□ FastAPI 프로젝트 스캐폴딩 + config, database, dependencies
□ Alembic 초기화 + 전체 테이블 마이그레이션 1회 실행
□ Next.js 프로젝트 초기 설정 (TypeScript + Tailwind)
□ .env.example 작성 (SUBSCRIPTION_LIMIT=5 포함)
□ git 초기화 + .gitignore

완료 기준: docker-compose up → FastAPI /docs 접근 가능
```

---

### Phase 1 — 더미 데이터 기반 핵심 화면 완성 (Day 3~10)

```
목표: 실제 API 없이도 핵심 3기능 화면을 모두 볼 수 있다
     사용자 피드백을 이 시점에서 받는다

[백엔드 - 실제 API]
□ auth 도메인 (register, login, JWT 7일)
□ users 도메인 (GET /users/me)
□ companies 도메인 (GET /companies, GET /companies/{id})
□ subscriptions 도메인 (GET/POST/DELETE)
□ 기업 시드 데이터 입력 (50개: 대기업 20 / 중견 15 / 공기업 15)

[백엔드 - 더미 데이터]
□ seeds/prep_snapshots.sql: 대기업 5개 prep 스냅샷 수동 작성
□ seeds/briefings.sql: 더미 브리핑 + 브리핑 아이템 3일치 수동 작성
  (삼성전자, 현대자동차, 카카오 각 뉴스 2건 + 채용 1건 기준)

[프론트엔드]
□ 로그인 / 회원가입 페이지
□ 기업 탐색 페이지 (목록 + 검색 + 카테고리 필터)
□ 기업 상세 카드 페이지 ← 더미 prep snapshot 포함 렌더링
  - 인재상, 뉴스 요약, 채용 흐름, 자소서 포인트, 면접 포인트
□ 관심기업 등록 버튼 + 내 관심기업 목록 페이지
□ 오늘의 브리핑 화면 ← 더미 브리핑 데이터 렌더링
  - 기업별 카드, 뉴스 항목, 채용공고 항목

완료 기준:
  "회원가입 → 기업 탐색 → 관심기업 등록 → 브리핑 화면 → 준비 카드"
  전체 흐름을 더미 데이터로 실제로 클릭하며 확인 가능

이 시점 사용자 피드백 수집:
  - 화면 구조가 직관적인가?
  - 브리핑 카드 형태가 읽기 편한가?
  - 준비 카드에서 가장 유용한 섹션이 무엇인가?
```

---

### Phase 2 — 실제 배치 자동화 (Day 11~17)

```
목표: 더미 데이터를 실제 수집 데이터로 교체한다

[배치]
□ collect_news.py (네이버 뉴스 API 연동)
□ collect_jobs.py
  - 대기업: 공식 채용사이트 RSS + 사람인 API
  - 중견기업: 사람인 API + 잡코리아 API
  - 공기업: 공공데이터포털 API → 공식사이트 → 사람인 순 fallback
□ generate_briefing.py (실제 수집 데이터 기반 브리핑 생성)
□ generate_prep.py (실제 데이터 기반 스냅샷 생성)
□ batch/run.py 진입점 + 로그 기록
□ cron 등록 (매일 06:00)

[검증]
□ 배치 수동 실행 → 실제 뉴스/채용공고 DB 저장 확인
□ 브리핑 페이지에서 실제 데이터 렌더링 확인
□ 더미 시드 데이터 제거 (또는 별도 플래그로 비활성화)

완료 기준: 배치 자동 실행 후 다음날 아침 실제 브리핑 확인 가능
```

---

### Phase 3 — 완성도 + 초기 출시 (Day 18~21)

```
목표: 실사용자 30명에게 공개

□ 전체 흐름 QA (회원가입 → 브리핑 → 준비카드 → 관심기업 해제)
□ Empty state UI (구독 없을 때, 브리핑 없을 때, 스냅샷 없을 때)
□ 에러 메시지 사용자 친화적으로 정리
□ 모바일 반응형 기본 처리
□ 서비스 배포 (Vercel + Railway 또는 Render)
□ 첫 사용자 30명 확보 (커뮤니티/오픈채팅 공유)

완료 기준: 외부 URL 공개 + 실사용자 30명 확보
```

---

### Phase 4 — 개선 (출시 이후)

```
사용자 피드백 기반 우선순위 결정:

□ Refresh Token 도입 (UX 개선)
□ Redis 캐싱 (트래픽 100명+ 대응)
□ OpenAI 연동 → 뉴스 자동 요약, 준비 포인트 고도화
□ 이메일 브리핑 발송 (SendGrid)
□ 관심기업 알림 설정 세분화 (기업별 ON/OFF)
□ 공기업 NCS / 시험유형 특화 분석
□ 면접 후기 기반 분석 (외부 데이터 연동)
□ 기업 추가 요청 기능
□ 관리자 어드민 화면
□ 모니터링 (Sentry, Grafana)
□ CI/CD 파이프라인 (GitHub Actions)
```

---

### 전체 타임라인

```
Day  1~ 2  │ Phase 0 │ 환경 설정
Day  3~10  │ Phase 1 │ ✅ 더미 데이터 기반 핵심 화면 완성 → 피드백 수집
Day 11~17  │ Phase 2 │ ✅ 실제 배치 자동화
Day 18~21  │ Phase 3 │ 🚀 초기 출시 (30명)
Day 22+    │ Phase 4 │ 피드백 기반 고도화
```

---

## 10. 제거/지연 항목 최종 정리

### 제거한 것 (MVP에 없음)

| 항목 | 이유 |
|------|------|
| Redis | 30명 수준에서 캐싱 불필요, 복잡성만 증가 |
| Refresh Token | 7일 Access Token으로 충분, Phase 4에서 도입 |
| OpenAI 뉴스 요약 | 비용 발생, MVP는 excerpt 직접 활용 |
| 이메일 브리핑 발송 | 서비스 내 retention 먼저 검증 |
| prep_contents 정적 구조 | 운영 부담 크고 최신성 보장 불가 |
| exam_analysis, review_summary 필드 | 수집 소스 없음, null 응답은 불필요한 프론트 처리 유발 |
| NCS 코드 저장/분류 | 별도 데이터 구조 필요, Phase 4로 이동 |
| 관리자 어드민 화면 | 시드 데이터는 SQL 직접 입력으로 대체 |

### Phase 2+ 로 이동한 것

| 항목 | 예상 시점 |
|------|----------|
| Refresh Token | Phase 4 |
| Redis 캐싱 | Phase 4 (100명+) |
| OpenAI 연동 | Phase 4 |
| 이메일 브리핑 | Phase 4 |
| 알림 설정 세분화 | Phase 4 |
| 공기업 NCS/시험유형 특화 | Phase 4 |
| 면접 후기 분석 | Phase 4+ |
| 전문 검색 (Elasticsearch) | Phase 5 |
| 유료 플랜 | Phase 5 |
| 모바일 앱 | Phase 6 |
