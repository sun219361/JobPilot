# 관심기업 브리핑 서비스 (Job Briefing Service)

> 취업 준비생을 위한 관심기업 브리핑 서비스
> 대기업 / 중견기업 / 공기업 취준생이 관심기업을 저장하고, 매일 최신 뉴스와 채용공고를 브리핑으로 받는 서비스

---

## 서비스 개요

**핵심 3기능**
1. **관심기업 등록** — 내가 준비할 기업을 고른다
2. **오늘의 브리핑** — 매일 아침 기업별 최신 소식이 쌓인다
3. **기업 준비 카드** — 뉴스 + 채용공고 기반 준비 가이드

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | FastAPI (Python) |
| DB | PostgreSQL |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Frontend | Next.js + TypeScript + Tailwind CSS |
| Batch | Python Script + Cron |
| Auth | JWT (Access Token, 7일) |
| Deploy | Vercel (Frontend) + Railway (Backend) |

---

## 프로젝트 구조

```
job-briefing-service/
├── docs/                    # 설계 문서
│   ├── architecture-v4.md   # 전체 아키텍처 (최신)
│   ├── api-spec.md          # API 명세
│   ├── db-schema.md         # DB 스키마
│   ├── batch-strategy.md    # 배치 수집 전략
│   └── roadmap.md           # 개발 로드맵
├── backend/                 # FastAPI 백엔드
├── frontend/                # Next.js 프론트엔드
└── README.md
```

---

## 설계 문서

| 문서 | 내용 |
|------|------|
| [architecture-v4.md](./docs/architecture-v4.md) | 전체 서비스 아키텍처, 도메인 구조, 폴더 구조 |
| [api-spec.md](./docs/api-spec.md) | API 엔드포인트 상세 명세 |
| [db-schema.md](./docs/db-schema.md) | DB 테이블 설계 및 DDL |
| [batch-strategy.md](./docs/batch-strategy.md) | 기업 유형별 수집 전략, 공기업 Fallback |
| [roadmap.md](./docs/roadmap.md) | 개발 로드맵 (Phase 0~4) |

---

## 개발 현황

- [x] 설계 문서 v4 완성 (2024-01)
- [ ] Phase 0: 환경 설정
- [ ] Phase 1: 더미 데이터 기반 핵심 화면
- [ ] Phase 2: 실제 배치 자동화
- [ ] Phase 3: 초기 출시 (30명)

---

## 핵심 설계 결정

| 결정 | 내용 |
|------|------|
| 관심기업 한도 | 기본 5개, 환경변수(SUBSCRIPTION_LIMIT)로 관리 |
| 더미 우선 개발 | 배치 자동화 전에 화면을 먼저 완성하여 피드백 수집 |
| prep 도메인 | 내부는 독립 도메인, API 응답에서는 companies/{id}에 포함 |
| MVP 응답 최소화 | Phase 2+ 기능은 응답 필드에서 완전 제거 (null 없음) |
| 공기업 fallback | 공공데이터포털 → 공식사이트 → 사람인 순 |
