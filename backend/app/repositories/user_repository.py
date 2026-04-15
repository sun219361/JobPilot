"""UserRepository – User 테이블 CRUD

제공 메서드:
- get_by_id(user_id)  : id로 User 조회 (없으면 None)
- get_by_email(email) : email로 User 조회 (없으면 None)
- create_user(email, password_hash, nickname) : 신규 User 생성 및 반환
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    # ── 조회 ──────────────────────────────────────────────────────────────

    def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._db.execute(stmt).scalar_one_or_none()

    # ── 생성 ──────────────────────────────────────────────────────────────

    def create_user(
        self,
        email: str,
        password_hash: str,
        nickname: str,
    ) -> User:
        """신규 User를 DB에 삽입하고 반환한다."""
        user = User(
            email=email,
            password_hash=password_hash,
            nickname=nickname,
            is_active=True,
        )
        self._db.add(user)
        self._db.flush()   # id 채번 (commit은 호출자가 담당)
        self._db.refresh(user)
        return user
