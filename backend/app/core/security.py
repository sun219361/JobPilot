"""security.py – JWT 토큰 생성/검증 + 비밀번호 해시/검증

사용 라이브러리:
- python-jose[cryptography]: JWT 생성 및 검증 (HS256)
- bcrypt (직접 사용): passlib 1.7.4 / bcrypt 5.x 호환성 문제로
  passlib 대신 bcrypt 라이브러리를 직접 호출한다.

설계:
- ACCESS_TOKEN만 구현 (refresh token 제외)
- payload: sub (user_id str), exp, iat, type="access"
- 비밀번호: bcrypt, rounds 기본값 사용
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# ── 비밀번호 해시/검증 ──────────────────────────────────────────────────


def hash_password(plain_password: str) -> str:
    """평문 비밀번호를 bcrypt hash로 변환한다."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문과 hash가 일치하는지 검증한다."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ── JWT 토큰 ──────────────────────────────────────────────────────────────

def create_access_token(
    subject: int | str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """JWT access token을 생성한다.

    Args:
        subject: user_id (str 또는 int — payload의 sub로 저장)
        extra_claims: 추가로 포함할 payload 키-값 (선택)

    Returns:
        JWT 문자열 (Bearer token 값)
    """
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": now,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """JWT access token을 디코딩하고 payload를 반환한다.

    Args:
        token: Bearer token 문자열

    Returns:
        decoded payload dict

    Raises:
        JWTError: 토큰이 유효하지 않거나 만료된 경우
    """
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
    )


def extract_user_id(token: str) -> int:
    """토큰에서 user_id(sub)를 추출한다.

    Args:
        token: Bearer token 문자열

    Returns:
        user_id (int)

    Raises:
        JWTError: 토큰 유효성 오류
        ValueError: sub가 없거나 int 변환 실패
    """
    payload = decode_access_token(token)
    sub = payload.get("sub")
    if sub is None:
        raise ValueError("token payload에 sub가 없습니다.")
    token_type = payload.get("type")
    if token_type != "access":
        raise ValueError(f"잘못된 token type: {token_type}")
    return int(sub)
