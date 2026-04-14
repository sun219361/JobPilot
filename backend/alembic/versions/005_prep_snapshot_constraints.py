"""005_prep_snapshot_constraints

Revision ID: 005_prep_snapshot_constraints
Revises: 004_company_job_postings
Create Date: 2026-04-14

Changes:
- prep_snapshots 테이블에 generation_date (DATE) 컬럼 추가
- prep_snapshots 테이블에 source_version (VARCHAR 30) 컬럼 추가
- (company_id, generation_date) UniqueConstraint 추가 → 하루 1개 snapshot 정책
- (company_id, generation_date) 복합 인덱스 추가 → latest snapshot 조회 최적화

기존 데이터 처리:
- generation_date: generated_at 컬럼의 날짜 부분으로 초기화
- source_version: 기존 row는 'seed'로 설정 (seed 또는 수동 데이터)
- 기존 데이터 중 같은 (company_id, generation_date) 중복이 있을 경우
  가장 최신 generated_at 1개만 남기고 나머지를 삭제 후 unique 제약 적용
"""

from alembic import op
import sqlalchemy as sa


revision = "005_prep_snapshot_constraints"
down_revision = "004_company_job_postings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. generation_date 컬럼 추가 (nullable 허용으로 시작 – 데이터 채운 후 NOT NULL로 변경)
    op.add_column(
        "prep_snapshots",
        sa.Column("generation_date", sa.Date(), nullable=True),
    )

    # 2. source_version 컬럼 추가
    op.add_column(
        "prep_snapshots",
        sa.Column("source_version", sa.String(30), nullable=True, server_default="seed"),
    )

    # 3. 기존 데이터의 generation_date를 generated_at 날짜로 초기화
    op.execute(
        """
        UPDATE prep_snapshots
        SET generation_date = (generated_at AT TIME ZONE 'UTC')::date
        WHERE generation_date IS NULL
        """
    )

    # 4. 기존 데이터 중 (company_id, generation_date) 중복 제거
    #    동일 날짜의 snapshot 중 id가 가장 큰(최신) 것만 남김
    op.execute(
        """
        DELETE FROM prep_snapshots
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM prep_snapshots
            GROUP BY company_id, generation_date
        )
        """
    )

    # 5. generation_date NOT NULL로 변경
    op.alter_column("prep_snapshots", "generation_date", nullable=False)

    # 6. UniqueConstraint 추가 (하루 1개 snapshot 정책)
    op.create_unique_constraint(
        "uq_prep_snapshots_company_date",
        "prep_snapshots",
        ["company_id", "generation_date"],
    )

    # 7. 복합 인덱스 추가 (latest snapshot 조회 최적화)
    op.create_index(
        "ix_prep_snapshots_company_date_desc",
        "prep_snapshots",
        ["company_id", "generation_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_prep_snapshots_company_date_desc", table_name="prep_snapshots")
    op.drop_constraint("uq_prep_snapshots_company_date", "prep_snapshots", type_="unique")
    op.drop_column("prep_snapshots", "generation_date")
    op.drop_column("prep_snapshots", "source_version")
