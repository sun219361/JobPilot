"""CompanyNews 모델 – 기업별 수집된 뉴스 기사"""

from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class CompanyNews(Base, TimestampMixin):
    __tablename__ = "company_news"
    __table_args__ = (
        UniqueConstraint("company_id", "duplicate_key", name="uq_company_news_company_dupe"),
        Index("ix_company_news_company_id", "company_id"),
        Index("ix_company_news_published_at", "published_at"),
        Index("ix_company_news_duplicate_key", "duplicate_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(200), nullable=True)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_name: Mapped[str] = mapped_column(String(50), nullable=False)
    # company_id + duplicate_key 기준 중복 방지
    # URL 정규화 hash 또는 title+date hash
    duplicate_key: Mapped[str] = mapped_column(String(64), nullable=False)

    # relationship
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company", back_populates="news_items", lazy="select"
    )
