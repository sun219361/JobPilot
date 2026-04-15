"""dependencies.py – FastAPI 공통 의존성

Phase 5: JWT Bearer 토큰 기반 실제 인증으로 교체.

변경 요약:
- oauth2_scheme: OAuth2PasswordBearer (tokenUrl="/api/v1/auth/login")
- get_current_user: Authorization: Bearer <token> 헤더를 검증하여 User 반환
  - 토큰 없음/유효하지 않음 → 401 Unauthorized
  - 토큰 유효하나 사용자 비활성 → 403 Forbidden
  - 사용자 미존재 → 401 Unauthorized
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import extract_user_id
from app.models.user import User

# tokenUrl 은 Swagger UI "Authorize" 버튼이 가리키는 로그인 엔드포인트
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """JWT access token을 검증하고 현재 사용자를 반환한다.

    Raises:
        401 Unauthorized: 토큰 없음 / 만료 / 형식 오류 / 사용자 미존재
        403 Forbidden:    사용자 계정 비활성(is_active=False)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 정보입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = extract_user_id(token)
    except (JWTError, ValueError):
        raise credentials_exception

    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다.",
        )

    return user
