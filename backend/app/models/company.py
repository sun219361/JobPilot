import enum

from sqlalchemy import String, Text, Boolean, Enum as SAEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class CompanyType(str, enum.Enum):
    LARGE = "LARGE"    # 대기업
    MID = "MID"        # 중견기업
    PUBLIC = "PUBLIC"  # 공기업


class Company(Base, TimestampMixin):
    __tablename__ = "companies"
    __table_args__ = (
        Index("ix_companies_name", "name"),
        Index("ix_companies_company_type", "company_type"),
        Index("ix_companies_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    company_type: Mapped[CompanyType] = mapped_column(
        SAEnum(CompanyType, name="companytype"), nullable=False
    )
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    homepage_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    careers_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # relationships
    subscriptions: Mapped[list["Subscription"]] = relationship(  # noqa: F821
        "Subscription", back_populates="company", lazy="select"
    )
    prep_snapshots: Mapped[list["PrepSnapshot"]] = relationship(  # noqa: F821
        "PrepSnapshot",
        back_populates="company",
        order_by="PrepSnapshot.generated_at.desc()",
        lazy="select",
    )
    briefing_items: Mapped[list["BriefingItem"]] = relationship(  # noqa: F821
        "BriefingItem", back_populates="company", lazy="select"
    )
    news_items: Mapped[list["CompanyNews"]] = relationship(  # noqa: F821
        "CompanyNews",
        back_populates="company",
        order_by="CompanyNews.published_at.desc()",
        lazy="select",
    )
    job_postings: Mapped[list["CompanyJobPosting"]] = relationship(  # noqa: F821
        "CompanyJobPosting",
        back_populates="company",
        order_by="CompanyJobPosting.posted_at.desc()",
        lazy="select",
    )
