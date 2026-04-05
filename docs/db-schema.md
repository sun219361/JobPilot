# DB 스키마 — MVP

> PostgreSQL 기준
> ORM: SQLAlchemy + Alembic 마이그레이션

---

## 전체 ERD 요약

```
users
 └── subscriptions (N) ──► companies
                                │
                    ┌───────────┴──────────┐
                    │                      │
              news_articles          job_postings
                    │                      │
                    └──────────┬───────────┘
                               ▼ (배치가 읽어 생성)
                         briefing_items
                               │
                           briefings ──► users
                         
                         prep_snapshots ──► companies
```

---

## DDL 전체

```sql
-- 확장 활성화 (한글 검색용)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ────────────────────────────
-- users
-- ────────────────────────────
CREATE TABLE users (
  id              SERIAL PRIMARY KEY,
  email           VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  name            VARCHAR(100) NOT NULL,
  is_active       BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────
-- companies
-- ────────────────────────────
CREATE TABLE companies (
  id          SERIAL PRIMARY KEY,
  name        VARCHAR(200) UNIQUE NOT NULL,
  slug        VARCHAR(200) UNIQUE NOT NULL,
  category    VARCHAR(20)  NOT NULL
                CHECK (category IN ('large', 'mid', 'public')),
  industry    VARCHAR(100),
  logo_url    TEXT,
  description TEXT,
  website_url TEXT,
  press_url   TEXT,           -- 공기업 보도자료 페이지 URL
  is_active   BOOLEAN DEFAULT TRUE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────
-- subscriptions
-- ────────────────────────────
CREATE TABLE subscriptions (
  id         SERIAL PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (user_id, company_id)
);

-- ────────────────────────────
-- news_articles
-- ────────────────────────────
CREATE TABLE news_articles (
  id           SERIAL PRIMARY KEY,
  company_id   INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  title        VARCHAR(500) NOT NULL,
  summary      TEXT,
  source_url   TEXT UNIQUE NOT NULL,
  source_name  VARCHAR(100),
  published_at TIMESTAMPTZ,
  collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────
-- job_postings
-- ────────────────────────────
CREATE TABLE job_postings (
  id           SERIAL PRIMARY KEY,
  company_id   INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  title        VARCHAR(500) NOT NULL,
  job_type     VARCHAR(30)
                CHECK (job_type IN ('full_time', 'internship', 'contract')),
  location     VARCHAR(100),
  source_url   TEXT UNIQUE NOT NULL,
  source_name  VARCHAR(100),
  posted_at    TIMESTAMPTZ,
  deadline_at  TIMESTAMPTZ,
  is_active    BOOLEAN DEFAULT TRUE,
  collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────
-- briefings
-- ────────────────────────────
CREATE TABLE briefings (
  id            SERIAL PRIMARY KEY,
  user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  briefing_date DATE NOT NULL,
  is_read       BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (user_id, briefing_date)
);

-- ────────────────────────────
-- briefing_items
-- (다형 ref_id 제거 → 명시적 FK 2개)
-- ────────────────────────────
CREATE TABLE briefing_items (
  id            SERIAL PRIMARY KEY,
  briefing_id   INTEGER NOT NULL REFERENCES briefings(id) ON DELETE CASCADE,
  company_id    INTEGER NOT NULL REFERENCES companies(id),
  item_type     VARCHAR(20) NOT NULL
                  CHECK (item_type IN ('news', 'job')),
  news_id       INTEGER REFERENCES news_articles(id) ON DELETE SET NULL,
  job_id        INTEGER REFERENCES job_postings(id)  ON DELETE SET NULL,
  -- 브리핑 시점 복사본 (원본 삭제 후에도 브리핑 내용 유지)
  title         VARCHAR(500) NOT NULL,
  summary       TEXT,
  source_url    TEXT,
  display_order SMALLINT DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT chk_item_ref CHECK (
    (item_type = 'news' AND news_id IS NOT NULL AND job_id IS NULL) OR
    (item_type = 'job'  AND job_id  IS NOT NULL AND news_id IS NULL)
  )
);

-- ────────────────────────────
-- prep_snapshots
-- (정적 콘텐츠가 아닌 배치 생성 결과물)
-- ────────────────────────────
CREATE TABLE prep_snapshots (
  id                  SERIAL PRIMARY KEY,
  company_id          INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  snapshot_date       DATE NOT NULL,
  talent_profile      TEXT,
  recent_news_summary TEXT,
  job_trend_summary   TEXT,
  resume_points       JSONB,
  interview_points    JSONB,
  data_sources        JSONB,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (company_id, snapshot_date)
);

-- ────────────────────────────
-- 인덱스
-- ────────────────────────────
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
CREATE INDEX idx_co_name_trgm  ON companies USING gin (name gin_trgm_ops);
```

---

## 설계 결정 사항

| 결정 | 이유 |
|------|------|
| `briefing_items.ref_id` 다형 참조 제거 | FK 무결성 불가, JOIN 불가, 명시적 FK 2개로 대체 |
| `briefing_items` 복사본 필드 유지 | 원본 뉴스/채용공고 삭제 후에도 브리핑 이력 유지 |
| `prep_snapshots` 날짜별 unique | 일별 이력 관리, 배치 재실행 시 upsert 가능 |
| `subscriptions` 알림 설정 컬럼 제거 | MVP는 모든 구독 동일, Phase 4에서 세분화 |
| `companies.press_url` 추가 | 공기업 보도자료 수집 지원 |
| `SUBSCRIPTION_LIMIT` DB 제약 없음 | 서비스 레이어 정책으로만 관리 (환경변수 기반) |
