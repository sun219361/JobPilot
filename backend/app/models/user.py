"""User 모델 – 인증 필드(password_hash) 포함

변경 이력:
- Phase 5: password_hash 필드 추가 (JWT 인증 지원)
  기존 seed user(id=1)는 migration에서 임시 hash로 초기화됨.
  seed.py 재실행 시 정상 hash로 덮어쓴다.
"""

from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    # bcrypt hash — 평문 저장 절대 금지
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── 관계 ──────────────────────────────────────────────────────
    subscriptions: Mapped[list["Subscription"]] = relationship(  # noqa: F821
        "Subscription", back_populates="user", lazy="select"
    )
    briefings: Mapped[list["Briefing"]] = relationship(  # noqa: F821
        "Briefing", back_populates="user", lazy="select"
    )
