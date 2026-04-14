"""repository.py – PrepSnapshot 배치 전용 DB 접근 레이어

역할:
- PrepSnapshot의 생성/조회/삭제 (배치 스크립트 전용)
- 뉴스/채용공고/회사 데이터 조회 (snapshot 생성용 원본 데이터)
- 구독 기업 목록 조회 (생성 대상 기업 필터링)

주의:
- FastAPI 런타임용 BriefingRepository / CompanyRepository 와 분리한다.
- 이 파일은 배치 스크립트(SessionLocal)에서 직접 호출한다.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select, func, distinct
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.company_job_posting import CompanyJobPosting, PostingStatus
from app.models.company_news import CompanyNews
from app.models.prep_snapshot import PrepSnapshot
from app.models.subscription import Subscription

logger = logging.getLogger(__name__)


class PrepSnapshotRepository:
    """PrepSnapshot 배치 전용 리포지토리."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── 대상 기업 조회 ────────────────────────────────────────────────

    def get_subscribed_companies(self) -> list[Company]:
        """관심기업으로 등록된 기업 목록 (중복 제거, 이름 오름차순).

        선택 정책: A – 관심기업으로 등록된 기업만 갱신.
        이유: MVP에서 전체 기업 일괄 갱신은 불필요한 연산.
             관심기업 데이터가 가장 최신이어야 하는 비즈니스 우선순위와 일치.
        """
        stmt = (
            select(Company)
            .where(
                Company.id.in_(select(distinct(Subscription.company_id))),
                Company.is_active == True,  # noqa: E712
            )
            .order_by(Company.name)
        )
        return list(self.db.scalars(stmt).all())

    def get_all_active_companies(self) -> list[Company]:
        """전체 활성 기업 목록 (이름 오름차순). PREP_TARGET_MODE=all 일 때 사용."""
        stmt = (
            select(Company)
            .where(Company.is_active == True)  # noqa: E712
            .order_by(Company.name)
        )
        return list(self.db.scalars(stmt).all())

    def get_company_by_id(self, company_id: int) -> Company | None:
        """특정 기업 조회 (--company-id 옵션용)."""
        return self.db.get(Company, company_id)

    # ── 원본 데이터 조회 ──────────────────────────────────────────────

    def get_recent_news(
        self,
        company_id: int,
        lookback_days: int,
        limit: int,
    ) -> list[CompanyNews]:
        """기업별 최근 N일 이내 뉴스 (published_at 최신순).

        Args:
            company_id: 기업 ID
            lookback_days: 최근 며칠 이내 (settings.prep_news_lookback_days)
            limit: 최대 조회 건수 (settings.prep_max_news_items)
        """
        since = datetime.now(tz=timezone.utc) - timedelta(days=lookback_days)
        stmt = (
            select(CompanyNews)
            .where(
                CompanyNews.company_id == company_id,
                CompanyNews.published_at >= since,
            )
            .order_by(CompanyNews.published_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_open_jobs(
        self,
        company_id: int,
        limit: int,
    ) -> list[CompanyJobPosting]:
        """기업별 OPEN 채용공고 (게시일 최신순).

        Args:
            company_id: 기업 ID
            limit: 최대 조회 건수 (settings.prep_max_job_items)
        """
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

    # ── PrepSnapshot 조회 ─────────────────────────────────────────────

    def get_snapshot_by_date(
        self,
        company_id: int,
        target_date: date,
    ) -> PrepSnapshot | None:
        """특정 날짜의 snapshot 조회 (daily 중복 체크용)."""
        stmt = select(PrepSnapshot).where(
            PrepSnapshot.company_id == company_id,
            PrepSnapshot.generation_date == target_date,
        )
        return self.db.scalar(stmt)

    def get_latest_snapshot(self, company_id: int) -> PrepSnapshot | None:
        """기업별 최신 snapshot 1개 조회."""
        stmt = (
            select(PrepSnapshot)
            .where(PrepSnapshot.company_id == company_id)
            .order_by(PrepSnapshot.generation_date.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    # ── PrepSnapshot 저장/삭제 ────────────────────────────────────────

    def create_snapshot(
        self,
        company_id: int,
        target_date: date,
        one_line_summary: str,
        recent_issue_summary: str,
        hiring_summary: str,
        talent_summary: str,
        cover_letter_points: list[str],
        interview_points: list[str],
        source_version: str = "auto_batch",
    ) -> PrepSnapshot:
        """새 PrepSnapshot 생성 후 세션에 추가 (commit은 호출자가 담당)."""
        now = datetime.now(tz=timezone.utc)
        snapshot = PrepSnapshot(
            company_id=company_id,
            generation_date=target_date,
            generated_at=now,
            created_at=now,
            one_line_summary=one_line_summary,
            recent_issue_summary=recent_issue_summary,
            hiring_summary=hiring_summary,
            talent_summary=talent_summary,
            cover_letter_points=cover_letter_points,
            interview_points=interview_points,
            source_version=source_version,
        )
        self.db.add(snapshot)
        return snapshot

    def delete_snapshot(self, snapshot: PrepSnapshot) -> None:
        """snapshot 삭제 (--overwrite 옵션용, commit은 호출자가 담당)."""
        self.db.delete(snapshot)
        self.db.flush()  # FK 제약 고려해 즉시 반영
        logger.debug(
            "snapshot 삭제: id=%d company_id=%d date=%s",
            snapshot.id, snapshot.company_id, snapshot.generation_date,
        )

    # ── 통계 ──────────────────────────────────────────────────────────

    def count_snapshots_by_company(self, company_id: int) -> int:
        """기업별 총 snapshot 개수 (모니터링/디버깅용)."""
        stmt = select(func.count()).where(
            PrepSnapshot.company_id == company_id
        )
        return self.db.scalar(stmt) or 0
