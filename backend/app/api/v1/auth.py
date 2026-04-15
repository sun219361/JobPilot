"""auth 라우터 – POST /api/v1/auth/signup, POST /api/v1/auth/login

설계:
- signup: email/password/nickname → 중복 검사 → User 생성 → success 응답
- login:  email/password → 인증 → JWT access token 반환

에러 응답은 공통 {"success": false, "error": {"code": ..., "message": ...}} 형식 사용.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.domains.auth.schemas import LoginRequest, SignupRequest, TokenResponse
from app.domains.auth.service import AuthService
from app.repositories.user_repository import UserRepository
from app.core.response import error_response, success_response

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post(
    "/signup",
    summary="회원가입",
    status_code=status.HTTP_201_CREATED,
)
def signup(
    body: SignupRequest,
    db: Session = Depends(get_db),
    auth_svc: AuthService = Depends(_get_auth_service),
):
    """신규 사용자를 등록한다.

    - 이메일 중복 시 409 Conflict
    - 비밀번호 최소 8자 미만 시 422 Unprocessable Entity (Pydantic 검증)
    """
    try:
        user = auth_svc.signup(
            email=body.email,
            password=body.password,
            nickname=body.nickname,
        )
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return success_response(
        data={"id": user.id, "email": user.email, "nickname": user.nickname}
    )


@router.post(
    "/login",
    summary="로그인 (JWT access token 발급)",
    response_model=None,
)
def login(
    body: LoginRequest,
    auth_svc: AuthService = Depends(_get_auth_service),
):
    """이메일/비밀번호로 로그인하고 JWT access token을 반환한다."""
    user = auth_svc.authenticate(email=body.email, password=body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_svc.create_token(user)
    return success_response(
        data=TokenResponse(access_token=token, token_type="bearer").model_dump()
    )
