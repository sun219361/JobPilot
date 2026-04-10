"""
collect_news.py – 관심기업 기준 뉴스 수집 배치

실행 방법:
  cd backend
  python -m app.scripts.news.collect_news
  python -m app.scripts.news.collect_news --company-id 1 --limit 3 --dry-run
  python -m app.scripts.news.collect_news --limit 10 --days 7

CLI 옵션:
  --company-id INT  특정 기업 ID만 수집 (미지정 시 관심기업 전체)
  --limit INT       기업당 최대 수집 개수 (기본값: settings.news_default_limit)
  --days INT        최근 며칠치 기사 기준 필터 (현재는 로그 표시용; 기본값: settings.news_lookback_days)
  --dry-run         저장 없이 수집 결과만 출력

cron 예시 (매일 오전 7시):
  0 7 * * * cd /path/to/backend && /path/to/.venv/bin/python -m app.scripts.news.collect_news >> /var/log/collect_news.log 2>&1
"""

import argparse
import logging
import sys
import os

# 프로젝트 루트를 sys.path에 추가 (직접 실행 시)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from sqlalchemy import select, distinct

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.company import Company
from app.models.subscription import Subscription
from app.scripts.news.providers.naver_news import NaverNewsProvider
from app.services.news_collection_service import NewsCollectionService, CollectionResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("collect_news")


def _get_target_companies(db, company_id: int | None) -> list[Company]:
    """수집 대상 기업 목록 반환.

    company_id 지정 시 해당 기업 1개만,
    미지정 시 현재 관심기업으로 등록된 기업 전체(중복 제거).
    """
    if company_id is not None:
        company = db.get(Company, company_id)
        if not company:
            logger.error("company_id=%d 기업을 찾을 수 없습니다.", company_id)
            return []
        return [company]

    # 관심기업으로 등록된 company_id 목록 (중복 제거)
    stmt = (
        select(Company)
        .where(
            Company.id.in_(
                select(distinct(Subscription.company_id))
            ),
            Company.is_active == True,  # noqa: E712
        )
        .order_by(Company.name)
    )
    return list(db.scalars(stmt).all())


def _build_provider():
    provider_name = settings.news_provider.lower()
    if provider_name == "naver":
        return NaverNewsProvider()
    raise ValueError(f"지원하지 않는 provider: {provider_name}")


def main():
    parser = argparse.ArgumentParser(description="관심기업 뉴스 수집 배치")
    parser.add_argument("--company-id", type=int, default=None, help="특정 기업 ID만 수집")
    parser.add_argument(
        "--limit",
        type=int,
        default=settings.news_default_limit,
        help=f"기업당 최대 수집 개수 (기본값: {settings.news_default_limit})",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=settings.news_lookback_days,
        help=f"최근 며칠치 기준 (기본값: {settings.news_lookback_days})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="저장 없이 수집 결과만 출력",
    )
    args = parser.parse_args()

    dry_run: bool = args.dry_run
    limit: int = args.limit
    days: int = args.days

    if dry_run:
        logger.info("=== DRY-RUN 모드: DB에 저장하지 않습니다 ===")

    db = SessionLocal()
    try:
        companies = _get_target_companies(db, args.company_id)

        if not companies:
            logger.warning("수집 대상 기업이 없습니다.")
            return

        logger.info(
            "수집 시작 – 대상 기업 %d개 | limit=%d | days=%d",
            len(companies), limit, days,
        )

        provider = _build_provider()
        service = NewsCollectionService(db, provider)

        results: list[CollectionResult] = []
        for company in companies:
            logger.info("── 수집 중: %s (id=%d)", company.name, company.id)
            result = service.collect_for_company(company, limit=limit, dry_run=dry_run)
            results.append(result)

        # ── 요약 출력 ──────────────────────────────────────
        print("\n" + "=" * 50)
        print(f"  수집 완료 요약 {'[DRY-RUN]' if dry_run else ''}")
        print("=" * 50)
        total_fetched = total_saved = total_skipped = 0
        for r in results:
            print(
                f"  [{r.company_id:>4}] {r.company_name:<20} "
                f"fetched={r.fetched:>3}  saved={r.saved:>3}  skipped={r.skipped:>3}"
            )
            total_fetched += r.fetched
            total_saved += r.saved
            total_skipped += r.skipped

        print("-" * 50)
        print(
            f"  합계: fetched={total_fetched}  saved={total_saved}  skipped={total_skipped}"
        )
        print("=" * 50 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()
