"""generate_prep_snapshots.py – 기업별 PrepSnapshot 자동 생성 배치

실행 방법:
  cd backend
  python -m app.scripts.prep.generate_prep_snapshots
  python -m app.scripts.prep.generate_prep_snapshots --company-id 31
  python -m app.scripts.prep.generate_prep_snapshots --dry-run
  python -m app.scripts.prep.generate_prep_snapshots --overwrite
  python -m app.scripts.prep.generate_prep_snapshots --date 2026-04-14
  python -m app.scripts.prep.generate_prep_snapshots --limit 10

CLI 옵션:
  --company-id INT  특정 기업 ID만 생성 (미지정 시 전체 대상 기업)
  --date YYYY-MM-DD snapshot 기준 날짜 (기본값: 오늘)
  --dry-run         저장 없이 생성 결과만 출력
  --overwrite       기존 당일 snapshot이 있어도 삭제 후 재생성
  --limit INT       처리할 최대 기업 수 제한

생성 대상 정책 (PREP_TARGET_MODE):
  subscriptions: 관심기업으로 등록된 기업만 갱신 (기본값, MVP 권장)
  all:           전체 활성 기업 갱신

중복/갱신 정책 (PREP_GENERATION_MODE):
  daily:  하루 1개 snapshot (기본값). --overwrite 없이 재실행 시 skip.
  always: 매 실행마다 새 snapshot 생성 (history 무제한 누적).

cron 예시 (매일 오전 8시 30분, 채용공고 수집 후 30분 뒤):
  30 8 * * * cd /home/user/webapp/backend && \\
    /home/user/webapp/backend/.venv/bin/python \\
    -m app.scripts.prep.generate_prep_snapshots >> /var/log/generate_prep_snapshots.log 2>&1
"""

import argparse
import logging
import sys
import os
from datetime import date

# ── 프로젝트 루트를 sys.path에 추가 ─────────────────────────────────────────
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    ),
)

from app.core.config import settings
from app.core.db import SessionLocal
from app.domains.prep.service import (
    PrepSnapshotGenerationService,
    SnapshotGenerationSummary,
    CompanySnapshotResult,
)

# ── 로깅 설정 ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("generate_prep_snapshots")


# ── 요약 출력 ─────────────────────────────────────────────────────────────


def _print_summary(summary: SnapshotGenerationSummary, dry_run: bool) -> None:
    tag = "[DRY-RUN] " if dry_run else ""
    sep = "=" * 65

    print()
    print(sep)
    print(f"  {tag}PrepSnapshot 생성 완료 요약 – {summary.target_date}")
    print(sep)
    print(f"  총 처리 기업        : {summary.total_companies}개")
    print(f"  ✅ 생성 완료        : {summary.created_count}개")
    print(f"  ⏭  기존 snapshot 건너뜀: {summary.skipped_existing_count}개")
    print(f"  📭 데이터 없어 건너뜀  : {summary.skipped_no_data_count}개")
    print(f"  ❌ 실패             : {summary.failed_count}개")
    print("-" * 65)

    if summary.created:
        print("  [생성 완료]")
        for r in summary.created:
            snap_info = f" → snapshot_id={r.snapshot_id}" if r.snapshot_id else " → dry_run"
            print(f"    company_id={r.company_id:<5} {r.company_name:<20}{snap_info}")

    if summary.skipped_existing:
        print("  [기존 snapshot 건너뜀]")
        for r in summary.skipped_existing:
            print(f"    company_id={r.company_id:<5} {r.company_name:<20} reason: {r.reason}")

    if summary.skipped_no_data:
        print("  [데이터 없어 건너뜀]")
        for r in summary.skipped_no_data:
            print(f"    company_id={r.company_id:<5} {r.company_name:<20} reason: {r.reason}")

    if summary.failed:
        print("  [실패]")
        for r in summary.failed:
            print(f"    company_id={r.company_id:<5} {r.company_name:<20} reason: {r.reason}")

    print(sep)
    print()


# ── 단일 기업 출력 ────────────────────────────────────────────────────────


def _print_single_result(result: CompanySnapshotResult, dry_run: bool) -> None:
    tag = "[DRY-RUN] " if dry_run else ""
    icon = {
        "created":          "✅",
        "skipped_existing": "⏭ ",
        "skipped_no_data":  "📭",
        "failed":           "❌",
    }.get(result.status, "?")

    print()
    print(f"  {tag}{icon} {result.status} – {result.company_name} (id={result.company_id})")
    if result.reason:
        print(f"    reason: {result.reason}")
    if result.snapshot_id:
        print(f"    snapshot_id: {result.snapshot_id}")
    print()


# ── 메인 ──────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="기업별 PrepSnapshot 자동 생성 배치",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--company-id", type=int, default=None, metavar="ID",
        help="특정 기업 ID만 생성 (미지정 시 전체 대상 기업)",
    )
    parser.add_argument(
        "--date", type=str, default=None, metavar="YYYY-MM-DD",
        help="snapshot 기준 날짜 (기본값: 오늘)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=False,
        help="저장 없이 생성 결과만 출력",
    )
    parser.add_argument(
        "--overwrite", action="store_true", default=False,
        help="기존 당일 snapshot이 있어도 삭제 후 재생성",
    )
    parser.add_argument(
        "--limit", type=int, default=None, metavar="N",
        help="처리할 최대 기업 수 제한",
    )
    args = parser.parse_args()

    # 날짜 파싱
    if args.date:
        try:
            target_date = date.fromisoformat(args.date)
        except ValueError:
            logger.error("날짜 형식 오류: %s (YYYY-MM-DD 형식으로 입력)", args.date)
            return 1
    else:
        target_date = date.today()

    dry_run: bool = args.dry_run
    overwrite: bool = args.overwrite

    logger.info(
        "PrepSnapshot 배치 시작 – date=%s company_id=%s "
        "dry_run=%s overwrite=%s limit=%s mode=%s",
        target_date,
        args.company_id or "ALL",
        dry_run,
        overwrite,
        args.limit or "없음",
        settings.prep_target_mode,
    )

    if dry_run:
        logger.info("=== DRY-RUN 모드: DB에 저장하지 않습니다 ===")

    db = SessionLocal()
    try:
        service = PrepSnapshotGenerationService(db)

        # 단일 기업 모드
        if args.company_id is not None:
            result = service.generate_for_company(
                company_id=args.company_id,
                target_date=target_date,
                dry_run=dry_run,
                overwrite=overwrite,
            )
            _print_single_result(result, dry_run)
            return 0 if result.status != "failed" else 1

        # 전체 기업 모드
        summary = service.generate_for_all(
            target_date=target_date,
            dry_run=dry_run,
            overwrite=overwrite,
            limit=args.limit,
        )
        _print_summary(summary, dry_run)

        return 1 if summary.failed_count > 0 else 0

    except Exception as exc:
        logger.exception("예상치 못한 오류: %s", exc)
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
