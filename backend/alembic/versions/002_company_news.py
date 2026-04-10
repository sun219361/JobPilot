"""add company_news table

Revision ID: 002_company_news
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "002_company_news"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "company_news",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column(
            "company_id",
            sa.Integer,
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("publisher", sa.String(200), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("source_name", sa.String(50), nullable=False),
        sa.Column("duplicate_key", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "company_id", "duplicate_key", name="uq_company_news_company_dupe"
        ),
    )
    op.create_index("ix_company_news_company_id", "company_news", ["company_id"])
    op.create_index("ix_company_news_published_at", "company_news", ["published_at"])
    op.create_index("ix_company_news_duplicate_key", "company_news", ["duplicate_key"])


def downgrade() -> None:
    op.drop_index("ix_company_news_duplicate_key", table_name="company_news")
    op.drop_index("ix_company_news_published_at", table_name="company_news")
    op.drop_index("ix_company_news_company_id", table_name="company_news")
    op.drop_table("company_news")
