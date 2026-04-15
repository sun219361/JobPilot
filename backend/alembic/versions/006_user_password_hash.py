"""006_user_password_hash

Revision ID: 006_user_password_hash
Revises: 005_prep_snapshot_constraints
Create Date: 2026-04-14

Changes:
- users 테이블에 password_hash (TEXT, NOT NULL) 컬럼 추가
- 기존 row(seed user id=1)는 임시 bcrypt hash로 초기화
  → seed.py 재실행 시 정상 비밀번호 hash로 교체됨

주의:
- 임시 hash는 'changeme_run_seed_again' 문자열의 bcrypt hash
- 운영 배포 전에 반드시 seed.py 또는 직접 비밀번호 변경 필요
"""

from alembic import op
import sqlalchemy as sa


revision = "006_user_password_hash"
down_revision = "005_prep_snapshot_constraints"
branch_labels = None
depends_on = None

# 'changeme_run_seed_again' 의 bcrypt hash (cost=12)
# python3 -c "from passlib.context import CryptContext; ctx=CryptContext(schemes=['bcrypt']); print(ctx.hash('changeme_run_seed_again'))"
_TEMP_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TiGBMkC1kS7QBxmOWOlvNMq6kHWi"


def upgrade() -> None:
    # 1. password_hash 컬럼 추가 (nullable 허용으로 시작)
    op.add_column(
        "users",
        sa.Column("password_hash", sa.Text(), nullable=True),
    )

    # 2. 기존 row에 임시 hash 설정
    op.execute(
        f"UPDATE users SET password_hash = '{_TEMP_HASH}' WHERE password_hash IS NULL"
    )

    # 3. NOT NULL 제약 적용
    op.alter_column("users", "password_hash", nullable=False)


def downgrade() -> None:
    op.drop_column("users", "password_hash")
