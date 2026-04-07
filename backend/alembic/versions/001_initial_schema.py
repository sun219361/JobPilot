"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── companytype enum (SQLAlchemy가 create_table 시 자동 생성하므로 수동 생성 불필요) ──

    # ── users ─────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("nickname", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ── companies ─────────────────────────────────────────
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("company_type", sa.Enum("LARGE", "MID", "PUBLIC", name="companytype"), nullable=False),
        sa.Column("industry", sa.String(100), nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("homepage_url", sa.String(500), nullable=True),
        sa.Column("careers_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_companies_name", "companies", ["name"])
    op.create_index("ix_companies_company_type", "companies", ["company_type"])
    op.create_index("ix_companies_is_active", "companies", ["is_active"])

    # ── subscriptions ─────────────────────────────────────
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("memo", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "company_id", name="uq_subscriptions_user_company"),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_company_id", "subscriptions", ["company_id"])

    # ── prep_snapshots ────────────────────────────────────
    op.create_table(
        "prep_snapshots",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("one_line_summary", sa.Text, nullable=False),
        sa.Column("recent_issue_summary", sa.Text, nullable=False),
        sa.Column("hiring_summary", sa.Text, nullable=False),
        sa.Column("talent_summary", sa.Text, nullable=False),
        sa.Column("cover_letter_points", sa.JSON, nullable=False),
        sa.Column("interview_points", sa.JSON, nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_prep_snapshots_company_id", "prep_snapshots", ["company_id"])
    op.create_index("ix_prep_snapshots_generated_at", "prep_snapshots", ["generated_at"])

    # ── briefings ─────────────────────────────────────────
    op.create_table(
        "briefings",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("briefing_date", sa.Date, nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_briefings_user_id", "briefings", ["user_id"])
    op.create_index("ix_briefings_briefing_date", "briefings", ["briefing_date"])

    # ── briefing_items ────────────────────────────────────
    op.create_table(
        "briefing_items",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("briefing_id", sa.Integer, sa.ForeignKey("briefings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("headline", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("action_point", sa.Text, nullable=True),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_briefing_items_briefing_id", "briefing_items", ["briefing_id"])
    op.create_index("ix_briefing_items_company_id", "briefing_items", ["company_id"])


def downgrade() -> None:
    op.drop_table("briefing_items")
    op.drop_table("briefings")
    op.drop_table("prep_snapshots")
    op.drop_table("subscriptions")
    op.drop_table("companies")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS companytype")
