from datetime import date, datetime

from sqlalchemy import ForeignKey, String, Text, Date, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Briefing(Base):
    __tablename__ = "briefings"
    __table_args__ = (
        Index("ix_briefings_user_id", "user_id"),
        Index("ix_briefings_briefing_date", "briefing_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    briefing_date: Mapped[date] = mapped_column(Date, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # relationships
    user: Mapped["User"] = relationship("User", back_populates="briefings")  # noqa: F821
    items: Mapped[list["BriefingItem"]] = relationship(
        "BriefingItem",
        back_populates="briefing",
        order_by="BriefingItem.sort_order",
        lazy="select",
        cascade="all, delete-orphan",
    )


class BriefingItem(Base):
    """
    브리핑 아이템 — snapshot 방식으로 저장.
    원본 뉴스/채용공고를 직접 참조하지 않고,
    브리핑 시점의 headline/summary/action_point를 복사 저장한다.
    company_id는 nullable FK로만 연결 (원본 삭제 시에도 브리핑 유지).
    """

    __tablename__ = "briefing_items"
    __table_args__ = (
        Index("ix_briefing_items_briefing_id", "briefing_id"),
        Index("ix_briefing_items_company_id", "company_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    briefing_id: Mapped[int] = mapped_column(
        ForeignKey("briefings.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), nullable=True
    )

    # snapshot 필드
    source_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # "news" | "job" | "notice"
    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    action_point: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # relationships
    briefing: Mapped["Briefing"] = relationship("Briefing", back_populates="items")
    company: Mapped["Company | None"] = relationship("Company", back_populates="briefing_items")  # noqa: F821
