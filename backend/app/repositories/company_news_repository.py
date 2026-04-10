"""CompanyNewsRepository – company_news 테이블 CRUD"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.company_news import CompanyNews


class CompanyNewsRepository:

    def __init__(self, db: Session):
        self.db = db

    # ── 중복 확인 ──────────────────────────────────────────

    def exists(self, company_id: int, duplicate_key: str) -> bool:
        stmt = select(func.count()).where(
            CompanyNews.company_id == company_id,
            CompanyNews.duplicate_key == duplicate_key,
        )
        return (self.db.scalar(stmt) or 0) > 0

    # ── 저장 ──────────────────────────────────────────────

    def create(
        self,
        company_id: int,
        title: str,
        url: str,
        published_at: datetime,
        source_name: str,
        duplicate_key: str,
        summary: str | None = None,
        publisher: str | None = None,
    ) -> CompanyNews:
        news = CompanyNews(
            company_id=company_id,
            title=title,
            url=url,
            published_at=published_at,
            source_name=source_name,
            duplicate_key=duplicate_key,
            summary=summary,
            publisher=publisher,
        )
        self.db.add(news)
        self.db.flush()
        self.db.refresh(news)
        return news

    # ── 조회 ──────────────────────────────────────────────

    def get_by_company(
        self,
        company_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[CompanyNews], int]:
        """기업별 최신 뉴스 목록 + 총 개수"""
        base = select(CompanyNews).where(CompanyNews.company_id == company_id)

        total: int = self.db.scalar(
            select(func.count()).select_from(base.subquery())
        ) or 0

        stmt = (
            base.order_by(CompanyNews.published_at.desc())
            .offset(offset)
            .limit(limit)
        )
        items = list(self.db.scalars(stmt).all())
        return items, total

    def get_recent_by_company(
        self,
        company_id: int,
        days: int = 7,
        limit: int = 20,
    ) -> list[CompanyNews]:
        """기업별 최근 N일 뉴스"""
        since = datetime.now(tz=timezone.utc) - timedelta(days=days)
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
