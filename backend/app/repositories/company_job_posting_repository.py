"""CompanyJobPostingRepository – 채용공고 DB 접근 레이어"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func, case
from sqlalchemy.orm import Session

from app.models.company_job_posting import CompanyJobPosting, PostingStatus


class CompanyJobPostingRepository:

    def __init__(self, db: Session):
        self.db = db

    # ── 중복 확인 ──────────────────────────────────────────────────

    def exists(self, company_id: int, duplicate_key: str) -> bool:
        """company_id + duplicate_key 기준 중복 존재 여부."""
        stmt = select(func.count()).where(
            CompanyJobPosting.company_id == company_id,
            CompanyJobPosting.duplicate_key == duplicate_key,
        )
        return (self.db.scalar(stmt) or 0) > 0

    def get_by_duplicate_key(
        self, company_id: int, duplicate_key: str
    ) -> CompanyJobPosting | None:
        """중복 키로 기존 공고 조회 (status 갱신용)."""
        stmt = select(CompanyJobPosting).where(
            CompanyJobPosting.company_id == company_id,
            CompanyJobPosting.duplicate_key == duplicate_key,
        )
        return self.db.scalar(stmt)

    # ── 저장 ──────────────────────────────────────────────────────

    def create(
        self,
        company_id: int,
        title: str,
        posting_url: str,
        source_name: str,
        duplicate_key: str,
        department: str | None = None,
        employment_type: str | None = None,
        location: str | None = None,
        responsibilities: str | None = None,
        qualifications: str | None = None,
        preferred: str | None = None,
        posted_at: datetime | None = None,
        deadline_at: datetime | None = None,
        status: PostingStatus = PostingStatus.OPEN,
        keywords: list[str] | None = None,
    ) -> CompanyJobPosting:
        posting = CompanyJobPosting(
            company_id=company_id,
            title=title,
            posting_url=posting_url,
            source_name=source_name,
            duplicate_key=duplicate_key,
            department=department,
            employment_type=employment_type,
            location=location,
            responsibilities=responsibilities,
            qualifications=qualifications,
            preferred=preferred,
            posted_at=posted_at,
            deadline_at=deadline_at,
            status=status,
            keywords=keywords,
        )
        self.db.add(posting)
        return posting

    def update_status(
        self, posting: CompanyJobPosting, status: PostingStatus
    ) -> None:
        """기존 공고의 status 갱신."""
        posting.status = status

    # ── 조회 ──────────────────────────────────────────────────────

    def get_by_company(
        self,
        company_id: int,
        limit: int = 20,
        offset: int = 0,
        open_first: bool = True,
    ) -> tuple[list[CompanyJobPosting], int]:
        """기업별 채용공고 목록 (OPEN 우선, 게시일 최신순).

        Returns:
            (postings, total_count)
        """
        stmt = select(CompanyJobPosting).where(
            CompanyJobPosting.company_id == company_id,
        )

        # 총 개수
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total: int = self.db.scalar(count_stmt) or 0

        # 정렬: OPEN 우선 + posted_at 최신순
        if open_first:
            # OPEN=0, UNKNOWN=1, CLOSED=2 로 정렬
            from sqlalchemy import case
            order_expr = case(
                (CompanyJobPosting.status == PostingStatus.OPEN,    0),
                (CompanyJobPosting.status == PostingStatus.UNKNOWN, 1),
                else_=2,
            )
            stmt = stmt.order_by(order_expr, CompanyJobPosting.posted_at.desc().nullslast())
        else:
            stmt = stmt.order_by(CompanyJobPosting.posted_at.desc().nullslast())

        stmt = stmt.offset(offset).limit(limit)
        postings = list(self.db.scalars(stmt).all())
        return postings, total

    def get_recent_by_company(
        self,
        company_id: int,
        days: int,
        limit: int = 10,
    ) -> list[CompanyJobPosting]:
        """기업별 최근 N일 이내 공고 (posted_at 최신순)."""
        since = datetime.now(tz=timezone.utc) - timedelta(days=days)
        stmt = (
            select(CompanyJobPosting)
            .where(
                CompanyJobPosting.company_id == company_id,
                CompanyJobPosting.posted_at >= since,
            )
            .order_by(CompanyJobPosting.posted_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_open_by_company(
        self,
        company_id: int,
        limit: int = 10,
    ) -> list[CompanyJobPosting]:
        """기업별 OPEN 상태 공고 (게시일 최신순)."""
        stmt = (
            select(CompanyJobPosting)
            .where(
                CompanyJobPosting.company_id == company_id,
                CompanyJobPosting.status == PostingStatus.OPEN,
            )
            .order_by(CompanyJobPosting.posted_at.desc().nullslast())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_expired_open_postings(
        self, company_id: int
    ) -> list[CompanyJobPosting]:
        """마감일이 지났지만 아직 OPEN 상태인 공고 목록 (status 갱신용)."""
        now = datetime.now(tz=timezone.utc)
        stmt = select(CompanyJobPosting).where(
            CompanyJobPosting.company_id == company_id,
            CompanyJobPosting.status == PostingStatus.OPEN,
            CompanyJobPosting.deadline_at != None,  # noqa: E711
            CompanyJobPosting.deadline_at < now,
        )
        return list(self.db.scalars(stmt).all())
