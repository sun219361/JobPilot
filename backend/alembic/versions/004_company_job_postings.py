"""add company_job_postings table

Revision ID: 004_company_job_postings
Revises: 003_briefing_constraints
Create Date: 2024-01-04 00:00:00.000000

변경 사항:
- company_job_postings 테이블 신규 생성
  - postingstatus enum (OPEN / CLOSED / UNKNOWN)
  - company_id + duplicate_key UniqueConstraint
  - keywords JSON 컬럼 (rule-based 키워드 태그)
  - status / posted_at / deadline_at 인덱스
  - (company_id, status, posted_at) 복합 인덱스 (OPEN 최신순 조회 최적화)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_company_job_postings"
down_revision: Union[str, None] = "003_briefing_constraints"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# PostgreSQL ENUM 타입 직접 정의 (create_type=False → 이미 존재하거나 외부에서 생성)
postingstatus_enum = postgresql.ENUM(
    "OPEN", "CLOSED", "UNKNOWN",
    name="postingstatus",
    create_type=False,  # 아래에서 명시적으로 CREATE TYPE 실행
)


def upgrade() -> None:
    # ── postingstatus enum 생성 (checkfirst로 중복 방지) ──────
    bind = op.get_bind()
    postingstatus_enum.create(bind, checkfirst=True)

    # ── company_job_postings 테이블 생성 ───────────────────
    op.create_table(
        "company_job_postings",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column(
            "company_id",
            sa.Integer,
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        # 공고 핵심 정보
        sa.Column("title",           sa.String(500), nullable=False),
        sa.Column("department",      sa.String(200), nullable=True),
        sa.Column("employment_type", sa.String(100), nullable=True),
        sa.Column("location",        sa.String(200), nullable=True),
        # 상세 텍스트
        sa.Column("responsibilities", sa.Text, nullable=True),
        sa.Column("qualifications",   sa.Text, nullable=True),
        sa.Column("preferred",        sa.Text, nullable=True),
        # 메타
        sa.Column("posting_url", sa.String(1000), nullable=False),
        sa.Column("source_name", sa.String(50),   nullable=False),
        sa.Column("posted_at",   sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        # status: create_type=False 로 위에서 이미 생성된 enum 재사용
        sa.Column(
            "status",
            postingstatus_enum,
            nullable=False,
            server_default="UNKNOWN",
        ),
        # 키워드 JSON
        sa.Column("keywords", sa.JSON, nullable=True),
        # 중복 방지 키
        sa.Column("duplicate_key", sa.String(64), nullable=False),
        # TimestampMixin
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        # Constraints
        sa.UniqueConstraint(
            "company_id", "duplicate_key",
            name="uq_job_postings_company_dupe",
        ),
    )

    # ── 인덱스 생성 ────────────────────────────────────────
    op.create_index("ix_job_postings_company_id",
                    "company_job_postings", ["company_id"])
    op.create_index("ix_job_postings_status",
                    "company_job_postings", ["status"])
    op.create_index("ix_job_postings_posted_at",
                    "company_job_postings", ["posted_at"])
    op.create_index("ix_job_postings_deadline_at",
                    "company_job_postings", ["deadline_at"])
    op.create_index("ix_job_postings_duplicate_key",
                    "company_job_postings", ["duplicate_key"])
    op.create_index(
        "ix_job_postings_company_status_posted",
        "company_job_postings",
        ["company_id", "status", "posted_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_job_postings_company_status_posted",
                  table_name="company_job_postings")
    op.drop_index("ix_job_postings_duplicate_key",
                  table_name="company_job_postings")
    op.drop_index("ix_job_postings_deadline_at",
                  table_name="company_job_postings")
    op.drop_index("ix_job_postings_posted_at",
                  table_name="company_job_postings")
    op.drop_index("ix_job_postings_status",
                  table_name="company_job_postings")
    op.drop_index("ix_job_postings_company_id",
                  table_name="company_job_postings")
    op.drop_table("company_job_postings")

    # enum 삭제 (다른 테이블에서 사용 안 함)
    postingstatus_enum.drop(op.get_bind(), checkfirst=True)
