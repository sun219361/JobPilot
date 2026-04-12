"""
BriefingGenerationRepository

브리핑 생성 배치에서 필요한 모든 DB 접근을 담당한다.
기존 BriefingRepository(API 조회 전용)와 분리해 책임을 명확히 한다.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select, func, distinct
from sqlalchemy.orm import Session

from app.models.briefing import Briefing, BriefingItem
from app.models.company import Company
from app.models.company_news import CompanyNews
from app.models.subscription import Subscription
from app.models.user import User


class BriefingGenerationRepository:

    def __init__(self, db: Session):
        self.db = db

    # ── 대상 사용자 ────────────────────────────────────────

    def get_users_with_subscriptions(self) -> list[User]:
        """관심기업이 1개 이상 있는 활성 사용자 목록"""
        stmt = (
            select(User)
            .where(
                User.is_active == True,  # noqa: E712
                User.id.in_(
                    select(distinct(Subscription.user_id))
                ),
            )
            .order_by(User.id)
        )
        return list(self.db.scalars(stmt).all())

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    # ── 관심기업 ───────────────────────────────────────────

    def get_subscribed_companies(
        self,
        user_id: int,
        limit: int | None = None,
    ) -> list[Company]:
        """사용자의 관심기업 목록 (등록일 최신순)"""
        stmt = (
            select(Company)
            .join(Subscription, Subscription.company_id == Company.id)
            .where(
                Subscription.user_id == user_id,
                Company.is_active == True,  # noqa: E712
            )
            .order_by(Subscription.created_at.desc())
        )
        if limit:
            stmt = stmt.limit(limit)
        return list(self.db.scalars(stmt).all())

    # ── 최근 뉴스 ──────────────────────────────────────────

    def get_recent_news_for_company(
        self,
        company_id: int,
        days: int,
        limit: int,
    ) -> list[CompanyNews]:
        """기업별 최근 N일 이내 뉴스 (published_at 최신순)"""
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

    # ── 중복 체크 ──────────────────────────────────────────

    def briefing_exists(self, user_id: int, briefing_date: date) -> bool:
        """해당 날짜에 이미 브리핑이 존재하는지 확인"""
        stmt = select(func.count()).where(
            Briefing.user_id == user_id,
            Briefing.briefing_date == briefing_date,
        )
        return (self.db.scalar(stmt) or 0) > 0

    def get_existing_briefing(self, user_id: int, briefing_date: date) -> Briefing | None:
        stmt = select(Briefing).where(
            Briefing.user_id == user_id,
            Briefing.briefing_date == briefing_date,
        )
        return self.db.scalar(stmt)

    # ── Briefing 저장 ──────────────────────────────────────

    def create_briefing(
        self,
        user_id: int,
        briefing_date: date,
        title: str,
    ) -> Briefing:
        briefing = Briefing(
            user_id=user_id,
            briefing_date=briefing_date,
            title=title,
            created_at=datetime.now(tz=timezone.utc),
        )
        self.db.add(briefing)
        self.db.flush()
        self.db.refresh(briefing)
        return briefing

    def delete_briefing(self, briefing: Briefing) -> None:
        """overwrite 모드에서 기존 브리핑 삭제 (cascade로 items도 삭제됨)"""
        self.db.delete(briefing)
        self.db.flush()

    # ── BriefingItem 저장 ──────────────────────────────────

    def create_briefing_item(
        self,
        briefing_id: int,
        company_id: int,
        news_id: int | None,
        source_type: str,
        headline: str,
        summary: str,
        sort_order: int,
        action_point: str | None = None,
    ) -> BriefingItem:
        item = BriefingItem(
            briefing_id=briefing_id,
            company_id=company_id,
            news_id=news_id,
            source_type=source_type,
            headline=headline,
            summary=summary,
            action_point=action_point,
            sort_order=sort_order,
            created_at=datetime.now(tz=timezone.utc),
        )
        self.db.add(item)
        return item
