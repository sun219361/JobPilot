from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import router as api_v1_router

# 모델 임포트 (Alembic이 모델을 인식하기 위해 필요)
import app.models  # noqa: F401


app = FastAPI(
    title="JobPilot API",
    description="취업 준비생용 관심기업 브리핑 서비스",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Phase 1에서 프론트 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 전역 예외 핸들러 ──────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {"code": "INTERNAL_ERROR", "message": "서버 오류가 발생했습니다."},
        },
    )


# HTTPException은 detail이 dict인 경우 그대로 error 필드로 반환
from fastapi.exceptions import RequestValidationError, HTTPException


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        error = detail
    else:
        error = {"code": "HTTP_ERROR", "message": str(detail)}
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": None, "error": error},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "입력값이 올바르지 않습니다.",
                "detail": exc.errors(),
            },
        },
    )


# ── 라우터 등록 ──────────────────────────────────────
app.include_router(api_v1_router)


# ── 헬스체크 ─────────────────────────────────────────
@app.get("/health", tags=["health"])
def health_check():
    return {"success": True, "data": {"status": "ok"}, "error": None}
