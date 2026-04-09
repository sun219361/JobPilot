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
# 마이그레이션 실행
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
```

### Subscriptions (관심기업)
```bash
# 관심기업 목록
GET /api/v1/subscriptions

# 관심기업 추가
POST /api/v1/subscriptions
Body: {"company_id": 1, "memo": "메모"}

# 관심기업 삭제
DELETE /api/v1/subscriptions/{subscription_id}
```

### Briefings (브리핑)
```bash
# 오늘의 브리핑
GET /api/v1/briefings/today
```

## 📊 데이터베이스

### 모델 구조
- **User**: 사용자 정보
- **Company**: 기업 정보 (이름, 유형, 산업, 요약)
- **Subscription**: 관심기업 등록 (user ↔ company)
- **PrepSnapshot**: 기업별 채용 준비 스냅샷
- **Briefing**: 날짜별 브리핑
- **BriefingItem**: 브리핑 아이템 (뉴스/채용공고)

### 마이그레이션
```bash
# 새 마이그레이션 생성
alembic revision --autogenerate -m "description"

# 마이그레이션 적용
alembic upgrade head

# 이전 버전으로 롤백
alembic downgrade -1
```

### 테스트 데이터
```bash
# seed 스크립트 실행 (기존 데이터 삭제 후 재생성)
python -m app.scripts.seed

# 포함 내용:
# - 1명의 테스트 유저 (dev@jobpilot.kr, id=1)
# - 30개 기업 (대기업 10, 중견기업 10, 공공기관 10)
# - 5개 기업의 PrepSnapshot
# - 오늘 날짜의 브리핑 (6개 아이템)
# - 3개 관심기업 등록
```

## 🏗️ 프로젝트 구조

```
backend/
├── app/
│   ├── api/v1/              # API 라우터
│   │   ├── companies.py     # 기업 엔드포인트
│   │   ├── subscriptions.py # 관심기업 엔드포인트
│   │   └── briefings.py     # 브리핑 엔드포인트
│   ├── core/                # 핵심 설정
│   │   ├── config.py        # 환경 설정
│   │   ├── db.py            # DB 연결
│   │   ├── dependencies.py  # FastAPI 의존성
│   │   └── response.py      # 응답 스키마
│   ├── models/              # SQLAlchemy 모델
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── subscription.py
│   │   ├── prep_snapshot.py
│   │   └── briefing.py
│   ├── schemas/             # Pydantic 스키마
│   │   ├── company.py
│   │   ├── subscription.py
│   │   └── briefing.py
│   ├── repositories/        # DB 접근 계층
│   │   ├── company_repository.py
│   │   ├── subscription_repository.py
│   │   └── briefing_repository.py
│   ├── services/            # 비즈니스 로직
│   │   ├── company_service.py
│   │   ├── subscription_service.py
│   │   └── briefing_service.py
│   ├── scripts/
│   │   └── seed.py          # 테스트 데이터 생성
│   └── main.py              # FastAPI 앱
├── alembic/                 # DB 마이그레이션
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## 🔧 환경 변수

```bash
# 애플리케이션 설정
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true

# 데이터베이스
DATABASE_URL=postgresql+psycopg2://jobpilot:jobpilot@localhost:5432/jobpilot
DATABASE_URL_ASYNC=postgresql+asyncpg://jobpilot:jobpilot@localhost:5432/jobpilot

# 비즈니스 규칙
SUBSCRIPTION_LIMIT=5  # 관심기업 최대 등록 개수
```

## 🔐 인증 (준비 단계)

현재는 `app/core/dependencies.py`의 `get_current_user`가 fake user (id=1)를 반환합니다.

**JWT 전환 방법:**
```python
# app/core/dependencies.py 수정

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401)
        return user
    except JWTError:
        raise HTTPException(status_code=401)
```

이 함수만 수정하면 모든 엔드포인트에 JWT 인증이 적용됩니다.

## 🧪 테스트

```bash
# Health check
curl http://localhost:8000/health

# 기업 목록
curl "http://localhost:8000/api/v1/companies?limit=5"

# 기업 검색 (한글 파라미터는 URL 인코딩 필요)
curl --get --data-urlencode "q=삼성" "http://localhost:8000/api/v1/companies"

# 기업 상세
curl "http://localhost:8000/api/v1/companies/31"

# 관심기업 목록
curl "http://localhost:8000/api/v1/subscriptions"

# 관심기업 추가
curl -X POST "http://localhost:8000/api/v1/subscriptions" \
  -H "Content-Type: application/json" \
  -d '{"company_id": 36}'

# 관심기업 삭제
curl -X DELETE "http://localhost:8000/api/v1/subscriptions/7"

# 오늘의 브리핑
curl "http://localhost:8000/api/v1/briefings/today"
```

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

## 📚 API 문서

서버 실행 후 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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

## 🔍 트러블슈팅

### PostgreSQL 연결 실패
```bash
# Docker 컨테이너 상태 확인
docker-compose ps

# PostgreSQL 로그 확인
docker-compose logs postgres

# 컨테이너 재시작
docker-compose restart postgres
```

### Import 에러
```bash
# 의존성 재설치
rm -rf .venv
uv sync
```

### 마이그레이션 충돌
```bash
# 현재 버전 확인
alembic current

# 특정 버전으로 이동
alembic downgrade <revision>
alembic upgrade <revision>
```

## 📝 개발 가이드

### 새 엔드포인트 추가

1. **모델 정의** (`app/models/`)
2. **스키마 정의** (`app/schemas/`)
3. **리포지토리 작성** (`app/repositories/`)
4. **서비스 로직 작성** (`app/services/`)
5. **라우터 작성** (`app/api/v1/`)
6. **마이그레이션 생성** (`alembic revision --autogenerate`)

### 비즈니스 규칙 변경

`app/core/config.py`의 `Settings` 클래스에서 환경변수로 제어할 수 있습니다.

---

**Last Updated:** 2026-04-09
