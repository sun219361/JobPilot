"""
BriefingGenerationService

뉴스 기반 브리핑 자동 생성 비즈니스 로직.
배치 스크립트(generate_today_briefings.py)에서 호출한다.

생성 규칙:
1. 관심기업이 1개 이상인 사용자만 대상
2. briefing_date 기준 1일 1 Briefing (중복 방지)
3. 기업당 최근 N일 이내 뉴스 M개 (published_at DESC)
4. 모든 관심기업에 뉴스가 하나도 없으면 Briefing 생성 안 함
   → "뉴스 없이 빈 브리핑"은 사용자에게 의미 없는 알림이 되므로 생략
5. ML 랭킹/감성분석 없음 — 최신순만 사용
"""

import logging
from dataclasses import dataclass, field
from datetime import date

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.briefing_generation_repository import BriefingGenerationRepository
from app.scripts.briefings.action_point import generate_action_point

logger = logging.getLogger(__name__)


@dataclass
class UserBriefingResult:
    user_id: int
    status: str          # "created" | "skipped_existing" | "skipped_no_news" | "failed"
    item_count: int = 0
    reason: str = ""


@dataclass
class BriefingGenerationSummary:
    target_date: date
    created: list[UserBriefingResult] = field(default_factory=list)
    skipped_existing: list[UserBriefingResult] = field(default_factory=list)
    skipped_no_news: list[UserBriefingResult] = field(default_factory=list)
    failed: list[UserBriefingResult] = field(default_factory=list)

    @property
    def total_users(self) -> int:
        return len(self.created) + len(self.skipped_existing) + len(self.skipped_no_news) + len(self.failed)


class BriefingGenerationService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = BriefingGenerationRepository(db)

    # ── 공개 메서드 ────────────────────────────────────────

    def generate_for_user(
        self,
        user_id: int,
        target_date: date,
        dry_run: bool = False,
        overwrite: bool = False,
    ) -> UserBriefingResult:
        """단일 사용자에 대해 브리핑을 생성한다."""
        try:
            return self._generate_for_user_internal(
                user_id=user_id,
                target_date=target_date,
                dry_run=dry_run,
                overwrite=overwrite,
            )
        except Exception as e:
            logger.error("브리핑 생성 실패 user_id=%d: %s", user_id, e, exc_info=True)
            if not dry_run:
                self.db.rollback()
            return UserBriefingResult(
                user_id=user_id,
                status="failed",
                reason=str(e),
            )

    def generate_for_all_users(
        self,
        target_date: date,
        dry_run: bool = False,
        overwrite: bool = False,
    ) -> BriefingGenerationSummary:
        """관심기업이 있는 모든 사용자에 대해 브리핑을 생성한다."""
        summary = BriefingGenerationSummary(target_date=target_date)
        users = self.repo.get_users_with_subscriptions()

        logger.info(
            "브리핑 생성 시작 – date=%s, users=%d, dry_run=%s, overwrite=%s",
            target_date, len(users), dry_run, overwrite,
        )

        for user in users:
            result = self.generate_for_user(
                user_id=user.id,
                target_date=target_date,
                dry_run=dry_run,
                overwrite=overwrite,
            )
            self._bucket_result(summary, result)

        return summary

    # ── 내부 로직 ──────────────────────────────────────────

    def _generate_for_user_internal(
        self,
        user_id: int,
        target_date: date,
        dry_run: bool,
        overwrite: bool,
    ) -> UserBriefingResult:
        # 1. 기존 브리핑 확인
        existing = self.repo.get_existing_briefing(user_id, target_date)
        if existing:
            if not overwrite:
                logger.info("SKIP existing – user_id=%d date=%s", user_id, target_date)
                return UserBriefingResult(
                    user_id=user_id,
                    status="skipped_existing",
                    reason=f"briefing_id={existing.id} already exists",
                )
            # overwrite: 기존 삭제
            if not dry_run:
                logger.info("OVERWRITE – 기존 브리핑 삭제 user_id=%d briefing_id=%d", user_id, existing.id)
                self.repo.delete_briefing(existing)

        # 2. 관심기업 조회 (최대 BRIEFING_MAX_COMPANIES_PER_USER개)
        companies = self.repo.get_subscribed_companies(
            user_id=user_id,
            limit=settings.briefing_max_companies_per_user,
        )
        if not companies:
            logger.info("SKIP no_subscriptions – user_id=%d", user_id)
            return UserBriefingResult(
                user_id=user_id,
                status="skipped_no_news",
                reason="no subscribed companies",
            )

        # 3. 기업별 뉴스 선별
        selected: list[tuple] = []  # (company, news_item)
        for company in companies:
            news_list = self.repo.get_recent_news_for_company(
                company_id=company.id,
                days=settings.briefing_news_lookback_days,
                limit=settings.briefing_max_items_per_company,
            )
            for news in news_list:
                selected.append((company, news))

        if not selected:
            logger.info("SKIP no_news – user_id=%d date=%s", user_id, target_date)
            return UserBriefingResult(
                user_id=user_id,
                status="skipped_no_news",
                reason="no recent news for any subscribed company",
            )

        # 4. dry_run 처리
        if dry_run:
            logger.info(
                "[DRY-RUN] user_id=%d date=%s → %d items (저장 생략)",
                user_id, target_date, len(selected),
            )
            for company, news in selected:
                logger.info(
                    "  [DRY-RUN]  %s | %s | %s",
                    company.name,
                    news.published_at.strftime("%Y-%m-%d"),
                    news.title[:60],
                )
            return UserBriefingResult(
                user_id=user_id,
                status="created",
                item_count=len(selected),
            )

        # 5. Briefing 생성
        title = f"{target_date.strftime('%Y년 %m월 %d일')} 관심기업 브리핑"
        briefing = self.repo.create_briefing(
            user_id=user_id,
            briefing_date=target_date,
            title=title,
        )

        # 6. BriefingItem 생성
        for sort_order, (company, news) in enumerate(selected, start=1):
            action_point = generate_action_point(
                source_type="news",
                company_name=company.name,
                headline=news.title,
            )
            self.repo.create_briefing_item(
                briefing_id=briefing.id,
                company_id=company.id,
                news_id=news.id,
                source_type="news",
                headline=news.title,
                summary=news.summary or news.title,
                sort_order=sort_order,
                action_point=action_point,
            )

        self.db.commit()
        logger.info(
            "CREATED – user_id=%d briefing_id=%d date=%s items=%d",
            user_id, briefing.id, target_date, len(selected),
        )
        return UserBriefingResult(
            user_id=user_id,
            status="created",
            item_count=len(selected),
        )

    @staticmethod
    def _bucket_result(
        summary: BriefingGenerationSummary,
        result: UserBriefingResult,
    ) -> None:
        bucket = getattr(summary, result.status, None)
        if bucket is not None:
            bucket.append(result)
        else:
            summary.failed.append(result)
