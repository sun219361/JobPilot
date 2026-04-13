"""JobCollectionService – 채용공고 수집 비즈니스 로직

배치 스크립트(collect_jobs.py)에서 호출한다.
FastAPI 런타임과는 무관하며, SessionLocal을 직접 사용한다.
"""

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.company import Company
from app.models.company_job_posting import PostingStatus
from app.repositories.company_job_posting_repository import CompanyJobPostingRepository
from app.scripts.jobs.duplicate_key import make_job_duplicate_key
from app.scripts.jobs.job_keywords import extract_keywords
from app.scripts.jobs.job_posting_item import JobPostingItem
from app.scripts.jobs.providers.base import BaseJobProvider

logger = logging.getLogger(__name__)


@dataclass
class JobCollectionResult:
    company_id: int
    company_name: str
    fetched: int           # provider가 반환한 총 개수
    saved: int             # 신규 저장 개수
    skipped: int           # 중복으로 건너뛴 개수
    status_updated: int    # 기존 공고 status 갱신 개수


class JobCollectionService:

    def __init__(self, db: Session, provider: BaseJobProvider):
        self.db = db
        self.repo = CompanyJobPostingRepository(db)
        self.provider = provider

    def collect_for_company(
        self,
        company: Company,
        limit: int = 5,
        dry_run: bool = False,
    ) -> JobCollectionResult:
        """단일 기업의 채용공고를 수집하고 신규 항목을 저장한다.

        수집 흐름:
        1. provider.fetch(company_name, limit) → JobPostingItem 리스트
        2. 각 item에 duplicate_key 생성
        3. 중복 없으면 키워드 추출 후 INSERT
        4. 중복이면 skip (status 갱신은 하지 않음 – 과도한 API 호출 방지)
        5. 마감일이 지난 OPEN 공고 자동 CLOSED 처리
        """
        raw_items: list[JobPostingItem] = self.provider.fetch(
            company.name, limit=limit
        )

        saved = 0
        skipped = 0
        status_updated = 0

        for item in raw_items:
            # duplicate_key 생성
            dup_key = make_job_duplicate_key(
                posting_url=item.posting_url,
                title=item.title,
                source_name=item.source_name,
                posted_at=item.posted_at,
            )
            item.duplicate_key = dup_key

            if self.repo.exists(company.id, dup_key):
                skipped += 1
                logger.debug(
                    "중복 공고 건너뜀: company=%s title=%s",
                    company.name, item.title[:40],
                )
                continue

            # 키워드 추출 (rule-based)
            extra_kws = [k.strip() for k in settings.job_keywords.split(",") if k.strip()]
            keywords = extract_keywords(
                title=item.title,
                responsibilities=item.responsibilities,
                qualifications=item.qualifications,
                preferred=item.preferred,
                extra_keywords=extra_kws,
            )

            if dry_run:
                logger.info(
                    "[DRY-RUN] 저장 생략 – company=%s | %s | %s | keywords=%s",
                    company.name,
                    item.posted_at.strftime("%Y-%m-%d") if item.posted_at else "날짜미상",
                    item.title[:60],
                    keywords,
                )
                saved += 1
                continue

            self.repo.create(
                company_id=company.id,
                title=item.title,
                posting_url=item.posting_url,
                source_name=item.source_name,
                duplicate_key=dup_key,
                department=item.department,
                employment_type=item.employment_type,
                location=item.location,
                responsibilities=item.responsibilities,
                qualifications=item.qualifications,
                preferred=item.preferred,
                posted_at=item.posted_at,
                deadline_at=item.deadline_at,
                status=PostingStatus.OPEN,
                keywords=keywords if keywords else None,
            )
            saved += 1
            logger.info(
                "공고 저장: company=%s | %s | %s | keywords=%s",
                company.name,
                item.posted_at.strftime("%Y-%m-%d") if item.posted_at else "날짜미상",
                item.title[:60],
                keywords,
            )

        # 마감일이 지난 OPEN 공고 → CLOSED 처리
        if not dry_run:
            expired = self.repo.get_expired_open_postings(company.id)
            for posting in expired:
                self.repo.update_status(posting, PostingStatus.CLOSED)
                status_updated += 1
                logger.info(
                    "마감 처리: company=%s | posting_id=%d | %s",
                    company.name, posting.id, posting.title[:40],
                )
            self.db.commit()
        else:
            # dry-run에서도 마감된 공고 정보는 출력
            expired = self.repo.get_expired_open_postings(company.id)
            if expired:
                logger.info(
                    "[DRY-RUN] 마감 처리 예정 공고 %d건 (company=%s)",
                    len(expired), company.name,
                )

        return JobCollectionResult(
            company_id=company.id,
            company_name=company.name,
            fetched=len(raw_items),
            saved=saved,
            skipped=skipped,
            status_updated=status_updated,
        )
