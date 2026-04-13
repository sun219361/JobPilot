"""
collect_jobs.py – 관심기업 기준 채용공고 수집 배치

실행 방법:
  cd backend
  python -m app.scripts.jobs.collect_jobs
  python -m app.scripts.jobs.collect_jobs --company-id 31 --limit 5 --dry-run
  python -m app.scripts.jobs.collect_jobs --limit 10 --days 30
  python -m app.scripts.jobs.collect_jobs --dry-run

CLI 옵션:
  --company-id INT  특정 기업 ID만 수집 (미지정 시 관심기업 전체)
  --limit INT       기업당 최대 수집 개수 (기본값: settings.job_default_limit)
  --days INT        최근 며칠치 기준 로그 표시 (현재 API 필터용)
  --dry-run         저장 없이 수집 결과만 출력

실행 예시:
  python -m app.scripts.jobs.collect_jobs
  python -m app.scripts.jobs.collect_jobs --company-id 31 --limit 5 --dry-run

cron 예시 (매일 오전 8시, 뉴스 수집 후 1시간 뒤):
  0 8 * * * cd /home/user/webapp/backend && \\
    /home/user/webapp/backend/.venv/bin/python \\
    -m app.scripts.jobs.collect_jobs >> /var/log/collect_jobs.log 2>&1
"""

import argparse
import logging
import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

from sqlalchemy import select, distinct

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.company import Company
from app.models.subscription import Subscription
from app.scripts.jobs.providers.saramin_provider import SaraminProvider
from app.services.job_collection_service import JobCollectionResult, JobCollectionService

# ── 로깅 설정 ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("collect_jobs")


# ── 대상 기업 조회 ─────────────────────────────────────────────────

def _get_target_companies(db, company_id: int | None) -> list[Company]:
    """수집 대상 기업 목록 반환.

    company_id 지정 시 해당 기업 1개,
    미지정 시 관심기업으로 등록된 전체(중복 제거, 이름 오름차순).
    """
    if company_id is not None:
        company = db.get(Company, company_id)
        if not company:
            logger.error("company_id=%d 기업을 찾을 수 없습니다.", company_id)
            return []
        return [company]

    stmt = (
        select(Company)
        .where(
            Company.id.in_(select(distinct(Subscription.company_id))),
            Company.is_active == True,  # noqa: E712
        )
        .order_by(Company.name)
    )
    return list(db.scalars(stmt).all())


# ── Provider 빌더 ──────────────────────────────────────────────────

def _build_provider():
    provider_name = settings.job_provider.lower()
    if provider_name == "saramin":
        return SaraminProvider()
    raise ValueError(f"지원하지 않는 job provider: {provider_name}")


# ── 요약 출력 ──────────────────────────────────────────────────────

def _print_summary(results: list[JobCollectionResult], dry_run: bool) -> None:
    tag = "[DRY-RUN] " if dry_run else ""
    print()
    print("=" * 65)
    print(f"  {tag}채용공고 수집 완료 요약")
    print("=" * 65)
    print(
        f"  {'기업':^4}  {'기업명':<20} {'수집':>5} {'저장':>5} "
        f"{'중복':>5} {'상태갱신':>7}"
    )
    print("-" * 65)

    total_fetched = total_saved = total_skipped = total_updated = 0
    for r in results:
        print(
            f"  [{r.company_id:>4}] {r.company_name:<20} "
            f"{r.fetched:>5}  {r.saved:>5}  {r.skipped:>5}  {r.status_updated:>7}"
        )
        total_fetched  += r.fetched
        total_saved    += r.saved
        total_skipped  += r.skipped
        total_updated  += r.status_updated

    print("-" * 65)
    print(
        f"  {'합계':<25} "
        f"{total_fetched:>5}  {total_saved:>5}  {total_skipped:>5}  {total_updated:>7}"
    )
    print("=" * 65)
    print()


# ── 메인 ──────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="관심기업 채용공고 수집 배치",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--company-id", type=int, default=None, metavar="ID",
        help="특정 기업 ID만 수집 (미지정 시 전체)",
    )
    parser.add_argument(
        "--limit", type=int, default=settings.job_default_limit,
        metavar="N",
        help=f"기업당 최대 수집 개수 (기본값: {settings.job_default_limit})",
    )
    parser.add_argument(
        "--days", type=int, default=settings.job_lookback_days,
        metavar="D",
        help=f"최근 며칠치 기준 (기본값: {settings.job_lookback_days})",
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=False,
        help="저장 없이 수집 결과만 출력",
    )
    args = parser.parse_args()

    dry_run: bool = args.dry_run
    limit: int = args.limit

    logger.info(
        "채용공고 수집 시작 – provider=%s limit=%d days=%d dry_run=%s",
        settings.job_provider, limit, args.days, dry_run,
    )
    if dry_run:
        logger.info("=== DRY-RUN 모드: DB에 저장하지 않습니다 ===")

    db = SessionLocal()
    try:
        companies = _get_target_companies(db, args.company_id)
        if not companies:
            logger.warning("수집 대상 기업이 없습니다.")
            return 0

        logger.info("대상 기업 %d개", len(companies))

        try:
            provider = _build_provider()
        except ValueError as e:
            logger.error("Provider 초기화 실패: %s", e)
            return 1

        service = JobCollectionService(db, provider)
        results: list[JobCollectionResult] = []

        for company in companies:
            logger.info("── 수집 중: %s (id=%d)", company.name, company.id)
            try:
                result = service.collect_for_company(
                    company, limit=limit, dry_run=dry_run
                )
                results.append(result)
            except Exception as e:
                logger.error(
                    "수집 실패 company=%s (id=%d): %s",
                    company.name, company.id, e, exc_info=True,
                )
                results.append(
                    JobCollectionResult(
                        company_id=company.id,
                        company_name=company.name,
                        fetched=0, saved=0, skipped=0, status_updated=0,
                    )
                )

        _print_summary(results, dry_run)
        return 0

    except Exception as e:
        logger.exception("예상치 못한 오류: %s", e)
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
