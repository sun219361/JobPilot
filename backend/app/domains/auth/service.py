"""AuthService – 회원가입, 로그인, 토큰 발급 비즈니스 로직

책임:
- signup        : email 중복 확인 → password hash → User 생성
- authenticate  : email/password 검증 → User 반환 (실패 시 None)
- create_token  : access token 문자열 반환 (security 모듈 위임)

에러 처리:
- 중복 email → ValueError("이미 사용 중인 이메일입니다.")
- 비밀번호 불일치 → None (router에서 401 처리)
"""

from __future__ import annotations

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    # ── 회원가입 ──────────────────────────────────────────────────────────

    def signup(self, email: str, password: str, nickname: str) -> User:
        """신규 사용자를 등록하고 생성된 User를 반환한다.

        Raises:
            ValueError: email이 이미 존재하는 경우
        """
        existing = self._user_repo.get_by_email(email)
        if existing is not None:
            raise ValueError("이미 사용 중인 이메일입니다.")

        password_hash = hash_password(password)
        return self._user_repo.create_user(
            email=email,
            password_hash=password_hash,
            nickname=nickname,
        )

    # ── 로그인 인증 ────────────────────────────────────────────────────────

    def authenticate(self, email: str, password: str) -> User | None:
        """email/password를 검증하고 일치하면 User를, 그렇지 않으면 None을 반환한다."""
        user = self._user_repo.get_by_email(email)
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    # ── 토큰 발급 ──────────────────────────────────────────────────────────

    def create_token(self, user: User) -> str:
        """User 정보로 JWT access token을 발급한다."""
        return create_access_token(
            subject=user.id,
            extra_claims={"email": user.email},
        )
