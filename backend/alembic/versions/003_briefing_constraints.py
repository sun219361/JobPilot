"""add briefing constraints and news_id to briefing_items

Revision ID: 003_briefing_constraints
Revises: 002_company_news
Create Date: 2024-01-03 00:00:00.000000
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "003_briefing_constraints"
down_revision: Union[str, None] = "002_company_news"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Briefing: user_id + briefing_date unique constraint 추가 ──────────
    op.create_unique_constraint(
        "uq_briefings_user_date", "briefings", ["user_id", "briefing_date"]
    )

    # ── BriefingItem: news_id FK 컬럼 추가 ────────────────────────────────
    op.add_column(
        "briefing_items",
        sa.Column(
            "news_id",
            sa.Integer,
            sa.ForeignKey("company_news.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    # ── BriefingItem: (briefing_id, sort_order) 복합 인덱스 추가 ─────────
    op.create_index(
        "ix_briefing_items_briefing_sort",
        "briefing_items",
        ["briefing_id", "sort_order"],
    )


def downgrade() -> None:
    op.drop_index("ix_briefing_items_briefing_sort", table_name="briefing_items")
    op.drop_column("briefing_items", "news_id")
    op.drop_constraint("uq_briefings_user_date", "briefings", type_="unique")
