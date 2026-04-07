from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_subscriptions_user_company"),
        Index("ix_subscriptions_user_id", "user_id"),
        Index("ix_subscriptions_company_id", "company_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)

    # relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")  # noqa: F821
    company: Mapped["Company"] = relationship("Company", back_populates="subscriptions")  # noqa: F821
