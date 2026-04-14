"""service.py – PrepSnapshot 배치 생성 오케스트레이션

역할:
- 기업 컨텍스트 조회 → generator 호출 → repository 저장
- 단일 기업 / 전체 기업 두 가지 진입점 제공
- dry_run / overwrite 플래그 지원
- 결과 집계 반환 (created, skipped_existing, skipped_no_data, failed)

설계 결정:
- 생성 대상 정책: A (관심기업만) 또는 C (전체) – PREP_TARGET_MODE로 제어
  → MVP 기본값: "subscriptions" (관심기업만)
  이유: 관심기업 데이터가 비즈니스상 최우선. 전체 갱신은 비용 대비 효과 낮음.

- 중복/갱신 정책: C (하루 1개, daily)
  → company_id + generation_date UNIQUE 제약으로 DB 레벨에서 보장.
  이유: 과도한 누적 방지, 일부 history 유지, --overwrite로 예외 처리 가능.
  "always" 모드도 지원 (PREP_GENERATION_MODE=always).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.domains.prep.generator import (
    CompanyContext,
    JobItem,
    NewsItem,
    generate_snapshot_fields,
)
from app.domains.prep.repository import PrepSnapshotRepository
from app.models.company import Company
from app.models.company_news import CompanyNews
from app.models.company_job_posting import CompanyJobPosting
from app.models.prep_snapshot import PrepSnapshot

logger = logging.getLogger(__name__)


# ── 결과 데이터 클래스 ────────────────────────────────────────────────────


@dataclass
class CompanySnapshotResult:
    """단일 기업 snapshot 생성 결과."""
    company_id: int
    company_name: str
    status: str   # "created" | "skipped_existing" | "skipped_no_data" | "failed"
    reason: str = ""
    snapshot_id: int | None = None


@dataclass
class SnapshotGenerationSummary:
    """전체 배치 실행 결과 요약."""
    target_date: date
    total_companies: int = 0
    created: list[CompanySnapshotResult]       = field(default_factory=list)
    skipped_existing: list[CompanySnapshotResult] = field(default_factory=list)
    skipped_no_data: list[CompanySnapshotResult]  = field(default_factory=list)
    failed: list[CompanySnapshotResult]        = field(default_factory=list)

    @property
    def created_count(self) -> int:
        return len(self.created)

    @property
    def skipped_existing_count(self) -> int:
        return len(self.skipped_existing)

    @property
    def skipped_no_data_count(self) -> int:
        return len(self.skipped_no_data)

    @property
    def failed_count(self) -> int:
        return len(self.failed)


# ── 서비스 클래스 ──────────────────────────────────────────────────────────


class PrepSnapshotGenerationService:
    """기업별 PrepSnapshot 생성 오케스트레이션 서비스.

    배치 스크립트(generate_prep_snapshots.py)에서만 사용한다.
    FastAPI 런타임과 무관하며 SessionLocal을 직접 주입받는다.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PrepSnapshotRepository(db)

    # ── 공개 API ──────────────────────────────────────────────────────

    def generate_for_company(
        self,
        company_id: int,
        target_date: date,
        dry_run: bool = False,
        overwrite: bool = False,
    ) -> CompanySnapshotResult:
        """단일 기업의 PrepSnapshot을 생성한다.

        Args:
            company_id: 생성할 기업 ID
            target_date: snapshot 기준 날짜
            dry_run: True이면 DB 저장 없이 생성 결과만 반환
            overwrite: True이면 당일 snapshot이 이미 있어도 삭제 후 재생성

        Returns:
            CompanySnapshotResult
        """
        company = self.repo.get_company_by_id(company_id)
        if not company:
            return CompanySnapshotResult(
                company_id=company_id,
                company_name=f"id={company_id}",
                status="failed",
                reason="company not found",
            )

        try:
            return self._generate_internal(company, target_date, dry_run, overwrite)
        except Exception as exc:
            logger.exception(
                "snapshot 생성 실패 company=%s (id=%d): %s",
                company.name, company_id, exc,
            )
            return CompanySnapshotResult(
                company_id=company_id,
                company_name=company.name,
                status="failed",
                reason=str(exc),
            )

    def generate_for_all(
        self,
        target_date: date,
        dry_run: bool = False,
        overwrite: bool = False,
        limit: int | None = None,
    ) -> SnapshotGenerationSummary:
        """설정된 대상 정책에 따라 기업 목록을 순회하며 snapshot을 생성한다.

        Args:
            target_date: snapshot 기준 날짜
            dry_run: True이면 DB 저장 없이 결과만 반환
            overwrite: True이면 기존 당일 snapshot 삭제 후 재생성
            limit: 처리할 최대 기업 수 (None이면 전체)

        Returns:
            SnapshotGenerationSummary
        """
        mode = settings.prep_target_mode.lower()
        if mode == "all":
            companies = self.repo.get_all_active_companies()
        else:
            companies = self.repo.get_subscribed_companies()

        if limit:
            companies = companies[:limit]

        summary = SnapshotGenerationSummary(
            target_date=target_date,
            total_companies=len(companies),
        )

        logger.info(
            "PrepSnapshot 배치 시작 – date=%s companies=%d "
            "mode=%s dry_run=%s overwrite=%s",
            target_date, len(companies), mode, dry_run, overwrite,
        )

        for company in companies:
            try:
                result = self._generate_internal(
                    company, target_date, dry_run, overwrite
                )
            except Exception as exc:
                logger.exception(
                    "snapshot 생성 실패 company=%s (id=%d): %s",
                    company.name, company.id, exc,
                )
                result = CompanySnapshotResult(
                    company_id=company.id,
                    company_name=company.name,
                    status="failed",
                    reason=str(exc),
                )

            _bucket_result(summary, result)

        return summary

    # ── 내부 로직 ──────────────────────────────────────────────────────

    def _generate_internal(
        self,
        company: Company,
        target_date: date,
        dry_run: bool,
        overwrite: bool,
    ) -> CompanySnapshotResult:
        """실제 snapshot 생성 흐름."""

        # 1. 중복 확인 (daily 정책)
        generation_mode = settings.prep_generation_mode.lower()
        if generation_mode == "daily":
            existing = self.repo.get_snapshot_by_date(company.id, target_date)
            if existing:
                if not overwrite:
                    logger.info(
                        "SKIP existing – company=%s (id=%d) date=%s snapshot_id=%d",
                        company.name, company.id, target_date, existing.id,
                    )
                    return CompanySnapshotResult(
                        company_id=company.id,
                        company_name=company.name,
                        status="skipped_existing",
                        reason=f"snapshot_id={existing.id} already exists",
                        snapshot_id=existing.id,
                    )
                # overwrite: 기존 삭제
                logger.info(
                    "OVERWRITE – 기존 snapshot 삭제: id=%d company=%s date=%s",
                    existing.id, company.name, target_date,
                )
                self.repo.delete_snapshot(existing)

        # 2. 원본 데이터 조회
        news_items = self.repo.get_recent_news(
            company.id,
            lookback_days=settings.prep_news_lookback_days,
            limit=settings.prep_max_news_items,
        )
        job_items = self.repo.get_open_jobs(
            company.id,
            limit=settings.prep_max_job_items,
        )

        # 3. 컨텍스트 DTO 변환
        ctx = CompanyContext(
            company_id=company.id,
            name=company.name,
            company_type=company.company_type,
            industry=company.industry,
            summary=company.summary or "",
            recent_news=[
                NewsItem(title=n.title, summary=n.summary)
                for n in news_items
            ],
            open_jobs=[
                JobItem(
                    title=j.title,
                    department=j.department,
                    employment_type=j.employment_type,
                    keywords=j.keywords or [],
                )
                for j in job_items
            ],
        )

        # 4. 규칙 기반 필드 생성
        fields = generate_snapshot_fields(ctx)

        # 5. dry_run: 저장 없이 결과 반환
        if dry_run:
            logger.info(
                "[DRY-RUN] company=%s (id=%d) | news=%d jobs=%d",
                company.name, company.id, len(news_items), len(job_items),
            )
            logger.info("  one_line   : %s", fields.one_line_summary[:60])
            logger.info("  issue      : %s", fields.recent_issue_summary[:60])
            logger.info("  hiring     : %s", fields.hiring_summary[:60])
            logger.info("  talent     : %s", fields.talent_summary[:60])
            logger.info("  cover(%d)  : %s", len(fields.cover_letter_points),
                        fields.cover_letter_points[:2])
            logger.info("  interview(%d): %s", len(fields.interview_points),
                        fields.interview_points[:2])
            return CompanySnapshotResult(
                company_id=company.id,
                company_name=company.name,
                status="created",
                reason="dry_run",
            )

        # 6. DB 저장
        snapshot = self.repo.create_snapshot(
            company_id=company.id,
            target_date=target_date,
            one_line_summary=fields.one_line_summary,
            recent_issue_summary=fields.recent_issue_summary,
            hiring_summary=fields.hiring_summary,
            talent_summary=fields.talent_summary,
            cover_letter_points=fields.cover_letter_points,
            interview_points=fields.interview_points,
            source_version="auto_batch",
        )
        self.db.commit()
        self.db.refresh(snapshot)

        logger.info(
            "snapshot 생성 완료: id=%d company=%s (id=%d) date=%s "
            "news=%d jobs=%d",
            snapshot.id, company.name, company.id,
            target_date, len(news_items), len(job_items),
        )

        return CompanySnapshotResult(
            company_id=company.id,
            company_name=company.name,
            status="created",
            snapshot_id=snapshot.id,
        )


# ── 헬퍼 ──────────────────────────────────────────────────────────────────


def _bucket_result(
    summary: SnapshotGenerationSummary,
    result: CompanySnapshotResult,
) -> None:
    """결과를 status 별로 summary 버킷에 분류한다."""
    mapping = {
        "created":          summary.created,
        "skipped_existing": summary.skipped_existing,
        "skipped_no_data":  summary.skipped_no_data,
        "failed":           summary.failed,
    }
    bucket = mapping.get(result.status, summary.failed)
    bucket.append(result)
