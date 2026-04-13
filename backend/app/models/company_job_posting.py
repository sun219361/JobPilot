"""CompanyJobPosting 모델 – 기업별 수집된 채용공고

설계 결정:
- keywords: 별도 CompanyJobKeyword 테이블 대신 JSON 컬럼에 저장
  이유: MVP에서 키워드는 읽기 전용 태그 역할. 별도 테이블로 분리하면
       JOIN 비용과 마이그레이션 복잡도만 늘어남. 향후 AI 분류/검색이
       필요해지면 그 시점에 별도 테이블로 추출하면 된다.

- status: PostingStatus enum (OPEN / CLOSED / UNKNOWN)
  DB에서 OPEN 우선 정렬·필터 시 enum이 string보다 안전하다.

- duplicate_key: company_id + duplicate_key UniqueConstraint
  URL 정규화 hash 또는 title+source_name+posted_at hash.
  CompanyNews와 동일한 전략 사용.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String, Text, DateTime, ForeignKey,
    UniqueConstraint, Index, Enum as SAEnum, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class PostingStatus(str, enum.Enum):
    OPEN    = "OPEN"     # 현재 모집 중
    CLOSED  = "CLOSED"   # 마감
    UNKNOWN = "UNKNOWN"  # 마감일 불명


class CompanyJobPosting(Base, TimestampMixin):
    """기업별 채용공고 스냅샷 테이블.

    수집 시점의 공고 내용을 저장한다.
    원본 URL이 사라져도 이력이 남는 snapshot 방식.
    """

    __tablename__ = "company_job_postings"
    __table_args__ = (
        # 동일 기업의 동일 공고 중복 방지
        UniqueConstraint(
            "company_id", "duplicate_key",
            name="uq_job_postings_company_dupe",
        ),
        Index("ix_job_postings_company_id",  "company_id"),
        Index("ix_job_postings_status",       "status"),
        Index("ix_job_postings_posted_at",    "posted_at"),
        Index("ix_job_postings_deadline_at",  "deadline_at"),
        Index("ix_job_postings_duplicate_key","duplicate_key"),
        # OPEN 공고를 최신순으로 자주 조회하므로 복합 인덱스 추가
        Index("ix_job_postings_company_status_posted",
              "company_id", "status", "posted_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # ── 기업 FK ─────────────────────────────────────────────
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    # ── 공고 핵심 정보 ────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    employment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 정규직/계약직/인턴
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # ── 상세 텍스트 (nullable – 일부 source는 제공 안 함) ─────
    responsibilities: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 담당업무
    qualifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)    # 자격요건
    preferred: Mapped[Optional[str]] = mapped_column(Text, nullable=True)         # 우대사항

    # ── 메타 ──────────────────────────────────────────────────
    posting_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_name: Mapped[str] = mapped_column(String(50), nullable=False)   # "saramin" 등

    posted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deadline_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    status: Mapped[PostingStatus] = mapped_column(
        SAEnum(PostingStatus, name="postingstatus"),
        default=PostingStatus.UNKNOWN,
        nullable=False,
    )

    # ── 키워드 (rule-based, JSON array) ──────────────────────
    # 예: ["Python", "SQL", "데이터분석"]
    # AI 분류가 아닌 사전 정의 keyword list 매칭 결과를 저장.
    keywords: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # ── 중복 방지 키 ───────────────────────────────────────────
    duplicate_key: Mapped[str] = mapped_column(String(64), nullable=False)

    # ── 관계 ──────────────────────────────────────────────────
    company: Mapped["Company"] = relationship(  # noqa: F821
        "Company", back_populates="job_postings", lazy="select"
    )
