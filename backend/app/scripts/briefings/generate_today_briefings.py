"""
generate_today_briefings.py
===========================
오늘 날짜의 브리핑을 생성하는 배치 스크립트.

사용법:
  # 전체 사용자 대상 (오늘 날짜)
  python -m app.scripts.briefings.generate_today_briefings

  # 특정 사용자만
  python -m app.scripts.briefings.generate_today_briefings --user-id 1

  # 특정 날짜 지정
  python -m app.scripts.briefings.generate_today_briefings --date 2024-03-15

  # dry-run (DB 저장 없이 미리보기)
  python -m app.scripts.briefings.generate_today_briefings --dry-run

  # 기존 브리핑 덮어쓰기 (재생성)
  python -m app.scripts.briefings.generate_today_briefings --overwrite

cron 예시 (매일 오전 7시):
  0 7 * * * cd /home/user/webapp/backend && \
    /home/user/webapp/backend/.venv/bin/python \
    -m app.scripts.briefings.generate_today_briefings \
    >> /var/log/generate_briefings.log 2>&1
"""

import argparse
import logging
import sys
from datetime import date

from app.core.db import SessionLocal
from app.services.briefing_generation_service import (
    BriefingGenerationService,
    BriefingGenerationSummary,
)

# ── 로깅 설정 ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("generate_briefings")


# ── CLI 인자 파싱 ──────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="오늘의 브리핑을 DB에 생성합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=None,
        metavar="USER_ID",
        help="특정 사용자 ID만 처리 (기본값: 전체 사용자)",
    )
    parser.add_argument(
        "--date",
        type=lambda s: date.fromisoformat(s),
        default=None,
        metavar="YYYY-MM-DD",
        help="브리핑 날짜 지정 (기본값: 오늘)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="DB에 저장하지 않고 미리보기만 출력",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="이미 존재하는 브리핑도 삭제 후 재생성",
    )
    return parser.parse_args()


# ── 요약 출력 ──────────────────────────────────────────────
def print_summary(summary: BriefingGenerationSummary, dry_run: bool) -> None:
    prefix = "[DRY-RUN] " if dry_run else ""
    total = summary.total_users

    logger.info("=" * 60)
    logger.info("%s브리핑 생성 완료 요약 – %s", prefix, summary.target_date)
    logger.info("=" * 60)
    logger.info("  총 처리 사용자     : %d명", total)
    logger.info("  ✅ 생성 완료       : %d명", len(summary.created))
    logger.info("  ⏭  기존 브리핑 건너뜀: %d명", len(summary.skipped_existing))
    logger.info("  📭 뉴스 없어 건너뜀  : %d명", len(summary.skipped_no_news))
    logger.info("  ❌ 실패            : %d명", len(summary.failed))

    if summary.created:
        logger.info("-" * 60)
        logger.info("[생성 완료 사용자]")
        for r in summary.created:
            logger.info("  user_id=%-4d  items=%d", r.user_id, r.item_count)

    if summary.skipped_existing:
        logger.info("-" * 60)
        logger.info("[기존 브리핑 건너뜀 사용자]")
        for r in summary.skipped_existing:
            logger.info("  user_id=%-4d  reason: %s", r.user_id, r.reason)

    if summary.skipped_no_news:
        logger.info("-" * 60)
        logger.info("[뉴스 없어 건너뜀 사용자]")
        for r in summary.skipped_no_news:
            logger.info("  user_id=%-4d  reason: %s", r.user_id, r.reason)

    if summary.failed:
        logger.info("-" * 60)
        logger.warning("[실패 사용자]")
        for r in summary.failed:
            logger.warning("  user_id=%-4d  error: %s", r.user_id, r.reason)

    logger.info("=" * 60)


# ── 단일 사용자 요약 출력 ──────────────────────────────────
def print_single_user_summary(
    result,
    target_date: date,
    dry_run: bool,
) -> None:
    prefix = "[DRY-RUN] " if dry_run else ""
    status_icon = {
        "created": "✅",
        "skipped_existing": "⏭ ",
        "skipped_no_news": "📭",
        "failed": "❌",
    }.get(result.status, "?")

    logger.info("=" * 60)
    logger.info("%s단일 사용자 브리핑 생성 – %s", prefix, target_date)
    logger.info("=" * 60)
    logger.info("  user_id   : %d", result.user_id)
    logger.info("  결과      : %s %s", status_icon, result.status)
    if result.item_count:
        logger.info("  아이템 수  : %d개", result.item_count)
    if result.reason:
        logger.info("  상세      : %s", result.reason)
    logger.info("=" * 60)


# ── 메인 ──────────────────────────────────────────────────
def main() -> int:
    args = parse_args()
    target_date: date = args.date or date.today()

    logger.info(
        "브리핑 생성 시작 – date=%s user_id=%s dry_run=%s overwrite=%s",
        target_date,
        args.user_id or "ALL",
        args.dry_run,
        args.overwrite,
    )

    db = SessionLocal()
    try:
        service = BriefingGenerationService(db)

        if args.user_id is not None:
            # 단일 사용자 처리
            result = service.generate_for_user(
                user_id=args.user_id,
                target_date=target_date,
                dry_run=args.dry_run,
                overwrite=args.overwrite,
            )
            print_single_user_summary(result, target_date, args.dry_run)
            # 실패면 비정상 종료 코드 반환
            return 1 if result.status == "failed" else 0

        else:
            # 전체 사용자 처리
            summary = service.generate_for_all_users(
                target_date=target_date,
                dry_run=args.dry_run,
                overwrite=args.overwrite,
            )
            print_summary(summary, args.dry_run)
            # 실패가 하나라도 있으면 비정상 종료 코드 반환
            return 1 if summary.failed else 0

    except Exception as e:
        logger.exception("예상치 못한 오류 발생: %s", e)
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
