# 개발 로드맵 — MVP

> **목표**: 실사용자 30명 확보
> **핵심 원칙**: 더미 데이터로 화면을 먼저 완성하고, 배치 자동화는 나중에 붙인다

---

## 핵심 개발 원칙

```
원칙 1: 더미 데이터로 화면을 먼저 완성한다
  배치 자동화 전에 사용자가 핵심 가치를 체감하게 한다.
  화면이 먼저 있어야 피드백도 빠르고 방향도 검증된다.

원칙 2: 실제 배치는 화면 완성 후 붙인다
  배치 자동화는 "완성된 화면에 데이터를 채우는 작업"이다.

원칙 3: 없는 기능은 보여주지 않는다
  Phase 2 이후 기능은 UI에도 없다. null 처리 UI도 없다.

원칙 4: 동작하는 서비스를 가장 빠르게
  인프라 완성 후 기능 개발이 아니라,
  동작하는 서비스를 먼저 만들고 다듬는다.
```

---

## Phase 0 — 환경 설정 (Day 1~2)

```
목표: 개발 환경 최소 세팅

□ docker-compose.yml (PostgreSQL 단독)
□ FastAPI 프로젝트 스캐폴딩
  - app/main.py, config.py, database.py, dependencies.py
□ Alembic 초기화 + 전체 테이블 마이그레이션 1회
□ Next.js 프로젝트 초기 설정 (TypeScript + Tailwind)
□ .env.example 작성 (SUBSCRIPTION_LIMIT=5 포함)
□ git 초기화 + .gitignore + GitHub 원격 연결
□ README.md 초안 작성

완료 기준:
  docker-compose up → FastAPI /docs 접근 가능
  Next.js 로컬 실행 가능
```

---

## Phase 1 — 더미 데이터 기반 핵심 화면 완성 (Day 3~10)

```
목표:
  실제 배치 없이도 핵심 3기능 화면을 모두 클릭하며 확인할 수 있다.
  이 단계에서 지인 5~10명에게 먼저 보여주고 피드백을 받는다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[백엔드] 실제 API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ auth 도메인 (register, login, JWT 7일)
□ users 도메인 (GET /users/me, PATCH, DELETE)
□ companies 도메인 (GET /companies, GET /companies/{id})
  └ companies.service에서 prep.repository.get_latest() 호출
□ subscriptions 도메인 (GET/POST/DELETE, SUBSCRIPTION_LIMIT 정책)
□ prep 도메인 (GET /prep/{company_id})
□ briefings 도메인 (GET /briefings, /briefings/today, /briefings/{id})

[백엔드] 더미 시드 데이터 (SQL 직접 입력)
□ seeds/companies.sql — 기업 50개 (대기업 20 / 중견 15 / 공기업 15)
□ seeds/prep_snapshots.sql — 대기업 5개 prep 스냅샷 수동 작성
  (삼성전자, 현대자동차, SK하이닉스, LG전자, 카카오)
□ seeds/briefings.sql — 더미 브리핑 3일치 수동 작성
  (삼성전자 뉴스 2건+채용 1건, 현대차 뉴스 1건+채용 1건, 카카오 뉴스 2건)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[프론트엔드] 핵심 화면 3개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
① 관심기업 등록 화면 (더미 기업 데이터)
  □ 기업 탐색 페이지 (목록 + 검색 + 카테고리 필터)
  □ 관심기업 등록/해제 버튼 (즉시 UI 반영)
  □ 내 관심기업 목록 ("3/5 사용 중" 표시)

② 기업 상세 카드 (더미 prep snapshot 포함)
  □ 기업 기본 정보 (로고, 이름, 업종)
  □ 인재상 섹션
  □ 최근 뉴스 요약 섹션
  □ 채용 흐름 요약 섹션
  □ 자소서 포인트 카드 (출처 표시)
  □ 면접 포인트 카드 (출처 표시)

③ 오늘의 브리핑 화면 (더미 브리핑 데이터)
  □ 기업별 카드 그룹 레이아웃
  □ 뉴스 아이템 (제목 + 요약 + 출처 링크)
  □ 채용공고 아이템 (마감일 강조)
  □ 읽음 처리 인터랙션

□ 로그인 / 회원가입 페이지
□ 대시보드 (관심기업 요약 + 오늘 브리핑 미리보기)

완료 기준:
  "회원가입 → 기업 탐색 → 관심기업 등록 → 오늘의 브리핑 → 기업 준비 카드"
  전체 흐름을 더미 데이터로 실제 클릭하며 확인 가능

이 시점 피드백 수집 항목:
  - 화면 구조가 직관적인가?
  - 브리핑 카드 형태가 읽기 편한가?
  - 준비 카드에서 가장 유용한 섹션은?
  - 빠진 기업이 있다면?
```

---

## Phase 2 — 실제 배치 자동화 (Day 11~17)

```
목표:
  더미 데이터를 실제 수집 데이터로 교체한다.
  매일 아침 실제 뉴스와 채용공고가 자동으로 쌓인다.

[배치]
□ batch/sources/base.py — 추상 수집기 인터페이스
□ batch/sources/large_corp.py — 네이버 뉴스 API + 공식사이트
□ batch/sources/mid_corp.py — 네이버 뉴스 API + 사람인 API
□ batch/sources/public_corp.py — 공공데이터포털 → 공식사이트 → 사람인 fallback
□ batch/tasks/collect_news.py
□ batch/tasks/collect_jobs.py
□ batch/tasks/generate_briefing.py
□ batch/tasks/generate_prep.py
□ batch/run.py — 진입점 + 로그 기록
□ cron 등록 (매일 06:00)

[검증]
□ 배치 수동 실행 → 실제 뉴스/채용공고 DB 저장 확인
□ 브리핑 페이지에서 실제 데이터 렌더링 확인
□ 더미 시드 브리핑 데이터 비활성화

완료 기준:
  배치 자동 실행 후 다음날 아침 실제 데이터 브리핑 확인 가능
```

---

## Phase 3 — 완성도 + 초기 출시 (Day 18~21)

```
목표: 실사용자 30명에게 공개

□ 전체 흐름 QA
  - 회원가입 → 기업탐색 → 구독 → 브리핑 → 준비카드 → 구독해제
□ Empty state UI 처리
  - 관심기업 0개일 때
  - 브리핑 없을 때 (no_subscription / pending_batch)
  - 준비 카드 스냅샷 없을 때
□ 에러 메시지 사용자 친화적으로 정리
□ 모바일 반응형 기본 처리
□ 서비스 배포 (Vercel + Railway 또는 Render)
□ 기업 시드 데이터 품질 검수
□ 첫 사용자 30명 확보 (커뮤니티/오픈채팅 공유)

완료 기준:
  외부 URL 공개 + 실사용자 30명 가입
```

---

## Phase 4 — 사용자 피드백 기반 개선 (출시 이후)

```
우선순위는 실사용자 피드백으로 결정한다.

UX 개선:
□ Refresh Token 도입
□ 기업 추가 요청 기능 (사용자가 원하는 기업 제안)

데이터 품질:
□ OpenAI 연동 → 뉴스 자동 요약, 준비 포인트 고도화
□ 이메일 브리핑 발송 (SendGrid)
□ 관심기업 알림 설정 세분화 (기업별 ON/OFF)
□ 공기업 NCS/시험유형 특화 분석

인프라:
□ Redis 캐싱 (트래픽 100명+ 대응)
□ 모니터링 (Sentry, Grafana)
□ CI/CD 파이프라인 (GitHub Actions)
□ 관리자 어드민 화면

수익화:
□ 유료 플랜 (SUBSCRIPTION_LIMIT_FREE=5, SUBSCRIPTION_LIMIT_PRO=20)
```

---

## 전체 타임라인

```
Day  1~ 2  │ Phase 0 │ 환경 설정
Day  3~10  │ Phase 1 │ ✅ 더미 데이터 기반 핵심 화면 → 초기 피드백 수집
Day 11~17  │ Phase 2 │ ✅ 실제 배치 자동화
Day 18~21  │ Phase 3 │ 🚀 초기 출시 (30명)
Day 22+    │ Phase 4 │ 피드백 기반 고도화
```

---

## 제거/지연 항목 최종 정리

### 제거한 것 (MVP에 없음)

| 항목 | 이유 |
|------|------|
| Redis | 30명 수준 캐싱 불필요, 복잡성만 증가 |
| Refresh Token | 7일 Access Token으로 충분 |
| OpenAI 요약 | 비용 발생, excerpt 직접 활용 |
| 이메일 브리핑 | 서비스 내 retention 먼저 검증 |
| prep_contents 정적 구조 | 운영 부담, 최신성 보장 불가 |
| exam_analysis / review_summary 필드 | 수집 소스 없음, null 응답 → 불필요한 프론트 처리 |
| NCS 코드 저장/분류 | 별도 구조 필요, Phase 4 |
| 관리자 어드민 화면 | SQL 직접 입력으로 대체 |
| Nginx 별도 설정 | Vercel + Railway로 단순화 |

### Phase 4+ 로 이동한 것

| 항목 | 예상 시점 |
|------|----------|
| Refresh Token | Phase 4 |
| Redis 캐싱 | Phase 4 |
| OpenAI 연동 | Phase 4 |
| 이메일 브리핑 | Phase 4 |
| 알림 설정 세분화 | Phase 4 |
| 공기업 NCS/시험유형 특화 | Phase 4 |
| 면접 후기 분석 | Phase 4+ |
| 전문 검색 (Elasticsearch) | Phase 5 |
| 유료 플랜 | Phase 5 |
| 모바일 앱 | Phase 6 |
