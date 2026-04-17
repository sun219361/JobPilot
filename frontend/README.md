# JobPilot Frontend

Next.js 14 App Router 기반의 취업 준비생 관심기업 브리핑 서비스 프론트엔드입니다.

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
npm install
```

### 2. 환경 설정

```bash
# .env.local 파일 생성
cp .env.example .env.local
```

**Mock 모드 (백엔드 불필요, 로그인 기능 비활성화):**
```bash
# .env.local
NEXT_PUBLIC_USE_MOCK=true
```

**Real API 모드 (백엔드 필요, JWT 인증 활성화):**
```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=false
```

### 3. 개발 서버 실행

```bash
# 개발 모드
npm run dev

# 프로덕션 빌드
npm run build
npm start

# PM2로 실행
pm2 start ecosystem.config.cjs
```

---

## 🔐 Phase 6: JWT 인증 (신규)

### 인증 흐름

```
회원가입 (/signup)
  → POST /api/v1/auth/signup (email, password, nickname)
  → 성공 시 자동 로그인

로그인 (/login)
  → POST /api/v1/auth/login (email, password)
  → access_token 반환 → localStorage 저장
  → GET /api/v1/users/me → 사용자 정보 저장

앱 시작 시 토큰 복원
  → localStorage에서 token 읽기
  → GET /api/v1/users/me 호출
  → 성공: 인증 상태 복원 / 실패: 토큰 삭제 + 비인증

로그아웃
  → localStorage에서 token 삭제 → 비인증 상태
```

### 보호된 페이지

| 페이지 | 경로 | AuthGuard |
|--------|------|-----------|
| 오늘의 브리핑 | `/briefings/today` | ✅ |
| 관심기업 관리 | `/subscriptions` | ✅ |

> 미인증 사용자가 보호된 페이지 접근 시 `/login`으로 자동 리다이렉트됩니다.

### 공개 페이지

| 페이지 | 경로 |
|--------|------|
| 홈 | `/` |
| 기업 상세 | `/companies/[id]` |
| 로그인 | `/login` |
| 회원가입 | `/signup` |

### 개발 시드 계정 (테스트용)

```
이메일: test@example.com
비밀번호: password1234
```

### curl 테스트 예시

```bash
# 1. 회원가입
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password1234", "nickname": "테스터"}'

# 2. 로그인 → 토큰 저장
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password1234"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])")

# 3. 현재 사용자 조회
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/users/me

# 4. 관심기업 목록 (Bearer 토큰 필요)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/subscriptions
```

### Fake User → JWT 전환 내용

| 항목 | 이전 (Phase 0) | 이후 (Phase 6) |
|------|---------------|----------------|
| 인증 방식 | 없음 (user_id=1 고정) | JWT Bearer Token |
| 토큰 저장 | N/A | localStorage |
| 보호 페이지 | 없음 | AuthGuard 컴포넌트 |
| 로그인 페이지 | 없음 | `/login` |
| 회원가입 | 없음 | `/signup` |
| 헤더 | 로그인/가입 링크 없음 | 상태에 따라 동적 변경 |
| API 헤더 | 없음 | Authorization: Bearer 자동 주입 |
| 401 처리 | N/A | 자동 로그아웃 |

---

## 📱 주요 페이지

### 1. 홈 (`/`)
- 서비스 소개 및 주요 기능 안내

### 2. 로그인 (`/login`)
- 이메일/비밀번호 입력
- 유효성 검사 (이메일 형식, 필수 입력)
- 에러 메시지 표시
- Mock 모드 안내
- 회원가입 페이지 링크

### 3. 회원가입 (`/signup`)
- 이메일, 닉네임, 비밀번호(8자↑), 비밀번호 확인
- 중복 이메일 감지 (409 에러 처리)
- 가입 후 자동 로그인 → `/briefings/today` 이동
- Mock 모드 안내

### 4. 관심기업 관리 (`/subscriptions`) 🔒
- **AuthGuard로 보호됨 (로그인 필요)**
- 등록된 관심기업 목록
- 기업 검색 및 추가 (최대 5개)
- 관심기업 삭제

### 5. 기업 상세 (`/companies/[id]`)
- 기업 기본 정보 및 채용 준비 스냅샷

### 6. 오늘의 브리핑 (`/briefings/today`) 🔒
- **AuthGuard로 보호됨 (로그인 필요)**
- 관심기업의 최신 뉴스·채용 공고 브리핑

---

## 🏗️ 프로젝트 구조

```
frontend/
├── app/                          # Next.js App Router
│   ├── page.tsx                  # 랜딩 페이지
│   ├── layout.tsx                # 루트 레이아웃 (AuthProvider 포함)
│   ├── login/
│   │   └── page.tsx              # 로그인 페이지 (신규)
│   ├── signup/
│   │   └── page.tsx              # 회원가입 페이지 (신규)
│   ├── subscriptions/
│   │   └── page.tsx              # 관심기업 관리 (AuthGuard 적용)
│   ├── companies/[id]/
│   │   └── page.tsx              # 기업 상세
│   └── briefings/today/
│       └── page.tsx              # 오늘의 브리핑 (AuthGuard 적용)
│
├── components/
│   ├── auth/                     # 인증 컴포넌트 (신규)
│   │   └── AuthGuard.tsx         # 미인증 리다이렉트 + 로딩 스켈레톤
│   ├── layout/
│   │   └── Navbar.tsx            # 인증 상태 표시 (신규: 닉네임/로그아웃)
│   ├── common/                   # 공통 컴포넌트
│   ├── subscriptions/
│   ├── companies/
│   └── briefings/
│
├── lib/
│   ├── api/
│   │   ├── config.ts             # API 설정
│   │   ├── http.ts               # HTTP 클라이언트 (Bearer 자동 주입, 401 처리)
│   │   ├── company-client.ts
│   │   ├── subscription-client.ts
│   │   ├── briefing-client.ts
│   │   └── mock/
│   ├── auth/                     # JWT 인증 모듈 (신규)
│   │   ├── token-storage.ts      # localStorage get/set/remove
│   │   ├── auth-client.ts        # signup, login, fetchMe API
│   │   ├── auth-context.tsx      # AuthProvider (React Context)
│   │   └── use-auth.ts           # useAuth() custom hook
│   ├── types/
│   │   └── index.ts              # 도메인 타입 (AuthUser, AuthState 등 포함)
│   ├── mock/
│   └── utils/
│
├── .env.example
├── .env.local
├── ecosystem.config.cjs          # PM2 설정
└── package.json
```

---

## 🔌 API 클라이언트 구조

### Bearer Token 자동 주입

`lib/api/http.ts`에서 모든 요청에 자동으로 Bearer 토큰을 주입합니다:

```typescript
// lib/api/http.ts
const token = getAccessToken(); // localStorage에서 읽기
const headers = {
  "Content-Type": "application/json",
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
};

// 401 발생 시 자동 로그아웃
if (response.status === 401) {
  localStorage.removeItem("jobpilot_access_token");
}
```

### AuthContext 흐름

```typescript
// 앱 시작 → 토큰 복원
useEffect(() => {
  fetchMe().then(me => {
    if (me) setAuthState("authenticated");
    else { removeAccessToken(); setAuthState("unauthenticated"); }
  });
}, []);
```

---

## 🧪 테스트 시나리오

1. **비인증 상태에서 보호 페이지 접근**
   - `/subscriptions` 또는 `/briefings/today` 직접 접근
   - → 자동으로 `/login` 리다이렉트 확인

2. **회원가입 → 자동 로그인**
   - `/signup`에서 새 계정 생성
   - → 가입 직후 `/briefings/today`로 이동 확인
   - → Navbar에 닉네임 표시 확인

3. **로그인 → 보호 페이지 접근**
   - `test@example.com` / `password1234` 로그인
   - → `/briefings/today` 접근 성공 확인

4. **잘못된 자격증명**
   - 틀린 이메일/비밀번호 입력
   - → "이메일 또는 비밀번호가 올바르지 않습니다" 에러 표시 확인

5. **로그아웃**
   - Navbar의 로그아웃 버튼 클릭
   - → 홈(`/`)으로 이동, 로그인/회원가입 링크 표시 확인

6. **새로고침 후 인증 상태 유지**
   - 로그인 후 브라우저 새로고침
   - → 여전히 로그인된 상태 유지 확인 (localStorage 토큰 복원)

---

## 🔍 트러블슈팅

### 빌드 오류
```bash
rm -rf .next && npm run build
```

### 로그인이 안 되는 경우
```bash
# Mock 모드 확인
cat .env.local | grep USE_MOCK
# NEXT_PUBLIC_USE_MOCK=false 여야 함

# 백엔드 상태 확인
curl http://localhost:8000/health
```

### 환경변수 미적용
```bash
npm run build && pm2 restart jobpilot-frontend
```

---

## 🌐 URL

| 환경 | URL |
|------|-----|
| 로컬 | http://localhost:3000 |
| 샌드박스 | https://3000-ix2krp6d80cvydxsp6ch8-b9b802c4.sandbox.novita.ai |

---

**Last Updated:** 2026-04-17  
**Framework:** Next.js 16.2.2  
**Phase:** 6 (JWT Authentication)

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
npm install
```

### 2. 환경 설정

```bash
# .env.local 파일 생성
cp .env.example .env.local
```

**Mock 모드 (백엔드 불필요):**
```bash
# .env.local
NEXT_PUBLIC_USE_MOCK=true
```

**Real API 모드 (백엔드 필요):**
```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=false
```

### 3. 개발 서버 실행

```bash
# 개발 모드
npm run dev

# 프로덕션 빌드
npm run build
npm start

# PM2로 실행
pm2 start ecosystem.config.cjs
```

## 📱 주요 페이지

### 1. 홈 (`/`)
- 서비스 소개 및 주요 기능 안내
- 관심기업 관리, 기업 상세, 브리핑으로 바로가기

### 2. 관심기업 관리 (`/subscriptions`)
- 등록된 관심기업 목록 표시
- 기업 검색 및 추가 (최대 5개)
- 관심기업 삭제
- 빈 상태 처리 (empty state)

### 3. 기업 상세 (`/companies/[id]`)
- 기업 기본 정보 (이름, 유형, 산업, 요약)
- 홈페이지/채용 페이지 링크
- 최신 채용 준비 스냅샷
  - 한 줄 요약
  - 최근 이슈
  - 채용 동향
  - 인재상
  - 자소서 포인트
  - 면접 포인트
- 관심기업 등록/해제 버튼

### 4. 오늘의 브리핑 (`/briefings/today`)
- 오늘 날짜의 브리핑 표시
- 관심기업별 뉴스/채용 공고 아이템
- 헤드라인, 요약, 액션 포인트
- 새로고침 기능

## 🏗️ 프로젝트 구조

```
frontend/
├── app/                          # Next.js App Router
│   ├── page.tsx                  # 랜딩 페이지
│   ├── layout.tsx                # 루트 레이아웃
│   ├── subscriptions/
│   │   └── page.tsx              # 관심기업 관리
│   ├── companies/[id]/
│   │   └── page.tsx              # 기업 상세
│   └── briefings/today/
│       └── page.tsx              # 오늘의 브리핑
│
├── components/
│   ├── common/                   # 공통 컴포넌트
│   │   ├── PageHeader.tsx        # 페이지 헤더
│   │   ├── LoadingSkeleton.tsx   # 스켈레톤 로더
│   │   ├── EmptyState.tsx        # 빈 상태
│   │   ├── ErrorState.tsx        # 에러 상태
│   │   └── Badge.tsx             # 뱃지 (기업 유형)
│   ├── subscriptions/
│   │   ├── SubscriptionCard.tsx  # 관심기업 카드
│   │   └── SubscriptionSearchPanel.tsx  # 기업 검색 패널
│   ├── companies/
│   │   ├── CompanyHero.tsx       # 기업 히어로 섹션
│   │   ├── PrepSnapshotCard.tsx  # 준비 스냅샷 카드
│   │   └── BulletPointList.tsx   # 포인트 리스트
│   └── briefings/
│       ├── BriefingHeader.tsx    # 브리핑 헤더
│       └── BriefingItemCard.tsx  # 브리핑 아이템 카드
│
├── lib/
│   ├── api/                      # API 클라이언트
│   │   ├── config.ts             # API 설정
│   │   ├── http.ts               # HTTP 클라이언트
│   │   ├── company-client.ts     # 기업 API
│   │   ├── subscription-client.ts # 관심기업 API
│   │   ├── briefing-client.ts    # 브리핑 API
│   │   └── mock/                 # Mock 구현
│   │       ├── company-client.ts
│   │       ├── subscription-client.ts
│   │       └── briefing-client.ts
│   ├── types/
│   │   ├── index.ts              # 도메인 타입
│   │   └── api.ts                # API 응답 타입
│   ├── mock/                     # Mock 데이터
│   │   ├── companies.ts
│   │   ├── subscriptions.ts
│   │   └── briefings.ts
│   └── utils/
│       └── format.ts             # 포맷 유틸리티
│
├── .env.example
├── .env.local
├── ecosystem.config.cjs          # PM2 설정
└── package.json
```

## 🔌 API 클라이언트 구조

### Mock/Real 자동 전환

환경변수 `NEXT_PUBLIC_USE_MOCK`에 따라 자동으로 클라이언트가 선택됩니다:

```typescript
// lib/api/company-client.ts
import { API_CONFIG } from "./config";
import { mockCompanyClient } from "./mock/company-client";

const realCompanyClient = {
  async getList({ q, company_type, limit, offset }) {
    return http.get("/api/v1/companies", { q, company_type, limit, offset });
  },
  async getById(id) {
    return http.get(`/api/v1/companies/${id}`);
  },
};

export const companyClient = API_CONFIG.USE_MOCK
  ? mockCompanyClient
  : realCompanyClient;
```

### HTTP 클라이언트

통일된 에러 처리와 응답 파싱:

```typescript
// lib/api/http.ts
export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public statusCode?: number
  ) {
    super(message);
  }
}

export const http = {
  get: <T>(endpoint: string, params?: object) => httpClient<T>(endpoint, { method: "GET", params }),
  post: <T>(endpoint: string, body?: unknown) => httpClient<T>(endpoint, { method: "POST", body }),
  delete: <T>(endpoint: string) => httpClient<T>(endpoint, { method: "DELETE" }),
};
```

## 🎨 컴포넌트 설계

### 상태 관리 원칙
- `loading`: 데이터 로딩 중
- `success`: 데이터 로드 성공
- `empty`: 데이터가 없음 (관심기업, 브리핑 등)
- `error`: 에러 발생
- `not-found`: 리소스를 찾을 수 없음 (기업 상세)

### 공통 컴포넌트

**PageHeader**
```tsx
<PageHeader
  title="페이지 제목"
  description="설명"
  action={<button>액션</button>}
/>
```

**LoadingSkeleton**
```tsx
<ListSkeleton count={3} Item={CompanyCardSkeleton} />
```

**EmptyState**
```tsx
<EmptyState
  icon="⭐"
  title="타이틀"
  description="설명"
  action={<button>액션</button>}
/>
```

**ErrorState**
```tsx
<ErrorState onRetry={load} />
```

## 🧪 개발 모드

### Mock 모드 (권장)
백엔드 없이 빠르게 UI 개발 및 테스트:

```bash
# .env.local
NEXT_PUBLIC_USE_MOCK=true

npm run dev
```

Mock 데이터는 `lib/mock/` 폴더에서 관리합니다.

### Real API 모드
실제 백엔드와 연동하여 테스트:

```bash
# 1. 백엔드 시작
cd ../backend
pm2 start ecosystem.config.cjs

# 2. 프론트엔드 설정
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=false

# 3. 프론트엔드 빌드 및 실행
npm run build
npm start
```

**중요:** 환경변수 변경 시 반드시 재빌드해야 합니다!

## 🚦 PM2 관리

```bash
# 시작
pm2 start ecosystem.config.cjs

# 상태 확인
pm2 list

# 로그 확인
pm2 logs jobpilot-frontend --nostream

# 재시작
pm2 restart jobpilot-frontend

# 중지
pm2 stop jobpilot-frontend

# 삭제
pm2 delete jobpilot-frontend
```

## 🌐 URL

### Local Development
- **Development**: http://localhost:3000
- **Production (PM2)**: http://localhost:3000

### Sandbox (Public)
- **Frontend**: https://3000-ix2krp6d80cvydxsp6ch8-b9b802c4.sandbox.novita.ai

## 🎯 사용자 시나리오

### 1. 관심기업 추가
1. `/subscriptions` 페이지 접속
2. "기업 추가" 버튼 클릭
3. 검색창에서 기업 검색
4. 원하는 기업의 "추가" 버튼 클릭
5. 관심기업 목록에 추가됨

### 2. 기업 정보 확인
1. 관심기업 카드 또는 검색 결과에서 기업 클릭
2. `/companies/[id]` 페이지로 이동
3. 기업 정보 및 채용 준비 스냅샷 확인
4. 홈페이지/채용 페이지 링크 클릭

### 3. 오늘의 브리핑 확인
1. `/briefings/today` 페이지 접속
2. 오늘 날짜의 브리핑 아이템 확인
3. 각 아이템의 헤드라인, 요약, 액션 포인트 읽기
4. 필요 시 새로고침 버튼으로 업데이트

## 🔍 트러블슈팅

### 빌드 오류
```bash
# 캐시 삭제 후 재빌드
rm -rf .next
npm run build
```

### 환경변수 미적용
```bash
# 환경변수 변경 시 반드시 재빌드
npm run build
pm2 restart jobpilot-frontend
```

### API 호출 실패 (Real API 모드)
```bash
# 백엔드 상태 확인
curl http://localhost:8000/health

# CORS 설정 확인 (backend/app/main.py)
# - allow_origins=["*"]
# - allow_credentials=True
```

## 🎨 스타일링

### Tailwind CSS
- 반응형 디자인 (mobile-first)
- 커스텀 컬러 없이 기본 팔레트 사용
- 간결하고 읽기 쉬운 레이아웃

### 디자인 원칙
- **카드 중심**: 정보는 카드 단위로 구성
- **고대비**: 텍스트 가독성 우선
- **최소 색상**: 회색 + 파란색 위주
- **명확한 계층**: 제목, 본문, 메타 정보 구분

## 📝 개발 가이드

### 새 페이지 추가

1. `app/` 폴더에 페이지 파일 생성
2. 필요한 컴포넌트 작성
3. API 클라이언트에 새 메서드 추가
4. Mock 클라이언트에 같은 인터페이스 구현

### 새 컴포넌트 추가

1. `components/` 적절한 폴더에 컴포넌트 생성
2. Props 타입 정의
3. Tailwind CSS로 스타일링
4. 다른 컴포넌트에서 import하여 사용

### API 클라이언트 수정

1. `lib/api/{client}.ts`에서 real 클라이언트 수정
2. `lib/api/mock/{client}.ts`에서 mock 클라이언트 동일하게 수정
3. 인터페이스 타입이 일치하는지 확인

---

**Last Updated:** 2026-04-09
**Framework:** Next.js 16.2.2
