from datetime import datetime

from sqlalchemy import ForeignKey, Text, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class PrepSnapshot(Base):
    """
    기업 준비 카드 스냅샷.
    배치가 생성하거나 seed로 직접 삽입한다.
    updated_at 없음 - 스냅샷은 불변(immutable)이며 날짜별로 새로 생성된다.
    """

    __tablename__ = "prep_snapshots"
    __table_args__ = (
        Index("ix_prep_snapshots_company_id", "company_id"),
        Index("ix_prep_snapshots_generated_at", "generated_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    one_line_summary: Mapped[str] = mapped_column(Text, nullable=False)
    recent_issue_summary: Mapped[str] = mapped_column(Text, nullable=False)
    hiring_summary: Mapped[str] = mapped_column(Text, nullable=False)
    talent_summary: Mapped[str] = mapped_column(Text, nullable=False)

    # PostgreSQL JSON 타입 — list[str] 형태로 저장
    cover_letter_points: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    interview_points: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # relationships
    company: Mapped["Company"] = relationship("Company", back_populates="prep_snapshots")  # noqa: F821
