"""PrepSnapshot – 기업별 준비 카드 스냅샷

설계 결정:
- snapshot은 기본적으로 불변(immutable). 날짜별로 최대 1개 생성 (daily 정책).
- source_version: 생성에 사용된 데이터 출처를 기록 (auto_batch / seed / manual).
  이력 추적 및 디버깅에 유용하며 모델 변경 없이 버전 구분 가능.
- generation_date: 생성 기준 날짜 (date 타입). company_id + generation_date 로
  하루 1개 unique 보장. generated_at(datetime)과 분리해 날짜 비교를 단순화.
- company_id + generation_date UniqueConstraint → 하루 1개 snapshot 정책 보장.
- (company_id, generation_date DESC) 복합 인덱스 → latest snapshot 조회 최적화.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    ForeignKey, Text, DateTime, Date, JSON,
    Index, UniqueConstraint, String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class PrepSnapshot(Base):
    """
    기업 준비 카드 스냅샷.
    배치(auto_batch) 또는 seed / 수동 삽입으로 생성된다.

    갱신 정책: 하루 1개 (company_id + generation_date UNIQUE).
    --overwrite 옵션 사용 시 기존 당일 snapshot을 삭제 후 재생성.
    """

    __tablename__ = "prep_snapshots"
    __table_args__ = (
        # 하루 1개 snapshot 정책 보장
        UniqueConstraint(
            "company_id", "generation_date",
            name="uq_prep_snapshots_company_date",
        ),
        # 기존 인덱스 유지
        Index("ix_prep_snapshots_company_id",   "company_id"),
        Index("ix_prep_snapshots_generated_at", "generated_at"),
        # latest snapshot 조회 최적화 복합 인덱스
        Index("ix_prep_snapshots_company_date_desc", "company_id", "generation_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    # ── 핵심 텍스트 필드 ──────────────────────────────────────────
    one_line_summary: Mapped[str] = mapped_column(Text, nullable=False)
    recent_issue_summary: Mapped[str] = mapped_column(Text, nullable=False)
    hiring_summary: Mapped[str] = mapped_column(Text, nullable=False)
    talent_summary: Mapped[str] = mapped_column(Text, nullable=False)

    # JSON 배열 (list[str])
    cover_letter_points: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    interview_points: Mapped[list]    = mapped_column(JSON, nullable=False, default=list)

    # ── 날짜/시각 ─────────────────────────────────────────────────
    # generation_date: 생성 기준 날짜 (unique 제약에 사용)
    generation_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # ── 출처 버전 ─────────────────────────────────────────────────
    # "auto_batch" | "seed" | "manual"
    source_version: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, default="auto_batch"
    )

    # ── 관계 ──────────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company", back_populates="prep_snapshots"
    )
