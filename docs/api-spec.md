# API 명세서 — MVP

> Base URL: `/api/v1`
> 인증: `Authorization: Bearer <access_token>`
> 버전: MVP (v4 설계 기준)

---

## 인증 (Auth)

### POST /auth/register
회원가입 후 Access Token 즉시 발급

**Request**
```json
{
  "email": "user@example.com",
  "password": "strongpassword123",
  "name": "홍길동"
}
```

**Response 201**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "홍길동"
  }
}
```

---

### POST /auth/login
로그인 후 Access Token 발급

**Request**
```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

**Response 200**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "홍길동"
  }
}
```

---

## 사용자 (Users)

### GET /users/me
내 프로필 조회

**Response 200**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "subscription_count": 3,
  "subscription_limit": 5,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### PATCH /users/me
이름 수정

**Request**
```json
{ "name": "홍길순" }
```

**Response 200**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길순"
}
```

---

### DELETE /users/me
회원 탈퇴

**Response 204** (No Content)

---

## 기업 (Companies)

### GET /companies
기업 목록 조회

**Query Parameters**
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| q | string | 기업명 검색 |
| category | string | large \| mid \| public |
| industry | string | IT/전자, 금융, 에너지 등 |
| page | int | 페이지 번호 (default: 1) |
| size | int | 페이지 크기 (default: 20) |

**Response 200**
```json
{
  "items": [
    {
      "id": 1,
      "name": "삼성전자",
      "slug": "samsung-electronics",
      "category": "large",
      "industry": "IT/전자",
      "logo_url": "...",
      "is_subscribed": true
    }
  ],
  "total": 50,
  "page": 1,
  "size": 20
}
```

---

### GET /companies/{id}
기업 상세 조회 (최신 prep snapshot 포함)

**Response 200 — prep snapshot 있을 때**
```json
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
  "prep_snapshot": {
    "snapshot_date": "2024-01-15",
    "talent_profile": "글로벌 기술 리더십과 창의적 문제해결 강조...",
    "recent_news_summary": "HBM4 양산 일정 발표...",
    "job_trend_summary": "DS부문 중심 채용 확대...",
    "resume_points": [
      { "point": "직무 연계 경험을 수치로 제시", "source": "채용공고 직무 기술서" }
    ],
    "interview_points": [
      { "point": "지원 직무의 최근 사업 방향 숙지", "source": "최근 뉴스 및 채용공고" }
    ],
    "data_sources": ["news_articles", "job_postings", "company_description"],
    "generated_at": "2024-01-15T06:30:00Z"
  }
}
```

**Response 200 — prep snapshot 없을 때**
```json
{
  "id": 1,
  "name": "삼성전자",
  ...
  "stats": { "latest_news_count": 0, "active_job_count": 0 }
  // prep_snapshot 키 자체 없음
}
```

---

## 구독 (Subscriptions)

### GET /subscriptions
내 관심기업 목록

**Response 200**
```json
{
  "items": [
    {
      "id": 10,
      "company": {
        "id": 1,
        "name": "삼성전자",
        "category": "large",
        "logo_url": "..."
      },
      "created_at": "2024-01-15T09:00:00Z"
    }
  ],
  "total": 3,
  "limit": 5
}
```

---

### POST /subscriptions
관심기업 등록

**Request**
```json
{ "company_id": 1 }
```

**Response 201**
```json
{
  "id": 10,
  "company": {
    "id": 1,
    "name": "삼성전자",
    "category": "large",
    "logo_url": "..."
  },
  "created_at": "2024-01-15T09:00:00Z"
}
```

**Error 422 — 한도 초과**
```json
{
  "error": {
    "code": "SUBSCRIPTION_LIMIT_EXCEEDED",
    "message": "관심기업은 최대 5개까지 등록할 수 있습니다.",
    "limit": 5,
    "current": 5
  }
}
```

**Error 409 — 중복**
```json
{
  "error": {
    "code": "DUPLICATE_SUBSCRIPTION",
    "message": "이미 등록된 관심기업입니다."
  }
}
```

---

### DELETE /subscriptions/{company_id}
관심기업 해제

**Response 204** (No Content)

---

## 브리핑 (Briefings)

### GET /briefings
내 브리핑 목록 (최근 30일)

**Response 200**
```json
{
  "items": [
    {
      "id": 100,
      "briefing_date": "2024-01-15",
      "is_read": false,
      "summary": {
        "total_items": 7,
        "news_count": 5,
        "job_count": 2,
        "companies_covered": 3
      }
    }
  ],
  "total": 14
}
```

---

### GET /briefings/today
오늘 브리핑

**Response 200 — 브리핑 있을 때**
```json
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
        },
        {
          "id": 202,
          "item_type": "job",
          "title": "2024 상반기 DS부문 신입공채",
          "summary": "마감: 2024-02-29 | 지원자격: 학사 이상",
          "source_url": "https://...",
          "display_order": 2
        }
      ]
    }
  ]
}
```

**Response 200 — 브리핑 없을 때**
```json
{
  "exists": false,
  "reason": "no_subscription",
  "message": "관심기업을 등록하면 내일 아침 첫 브리핑이 시작됩니다."
}
```

```json
{
  "exists": false,
  "reason": "pending_batch",
  "message": "오늘 브리핑을 준비 중입니다. 잠시 후 확인해주세요."
}
```

---

### GET /briefings/{id}
특정 브리핑 상세

**Response**: `/briefings/today`와 동일한 구조 (exists 필드 없음)

---

### PATCH /briefings/{id}/read
읽음 처리

**Response 200**
```json
{ "id": 100, "is_read": true }
```

---

## 준비 카드 (Prep)

### GET /prep/{company_id}
기업 준비 카드 최신 스냅샷

**Response 200 — 스냅샷 있을 때**
```json
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
    { "point": "공식 채용사이트 직무 소개 섹션 정독", "source": "공식 채용사이트" }
  ],
  "data_sources": ["news_articles", "job_postings", "company_description"],
  "generated_at": "2024-01-15T06:30:00Z"
}
```

**Response 200 — 스냅샷 없을 때**
```json
{
  "company": { "id": 1, "name": "삼성전자" },
  "exists": false,
  "message": "준비 카드는 매일 새벽 업데이트됩니다."
}
```

**후속 필드 (Phase 2+ 이후 추가 예정, MVP 응답에 포함하지 않음)**
- `exam_analysis`: 필기시험 유형 분석
- `review_summary`: 면접 후기 기반 분석
- `competitor_insight`: 경쟁사 비교 분석

---

## 에러 코드 전체 목록

| HTTP | Code | 발생 상황 |
|------|------|----------|
| 400 | `VALIDATION_ERROR` | 입력값 오류 |
| 401 | `UNAUTHORIZED` | 토큰 없음 |
| 401 | `TOKEN_EXPIRED` | 토큰 만료 |
| 404 | `COMPANY_NOT_FOUND` | 기업 없음 |
| 404 | `BRIEFING_NOT_FOUND` | 브리핑 없음 |
| 409 | `DUPLICATE_SUBSCRIPTION` | 중복 구독 |
| 422 | `SUBSCRIPTION_LIMIT_EXCEEDED` | 구독 한도 초과 |
| 500 | `INTERNAL_ERROR` | 서버 오류 |
