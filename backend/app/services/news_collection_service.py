"""NewsCollectionService – 뉴스 수집 비즈니스 로직

배치 스크립트(collect_news.py)에서 호출한다.
FastAPI 런타임과는 무관하며, SessionLocal을 직접 사용한다.
"""

import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.company import Company
from app.repositories.company_news_repository import CompanyNewsRepository
from app.scripts.news.duplicate_key import make_duplicate_key
from app.scripts.news.news_item import NewsItem
from app.scripts.news.providers.base import BaseNewsProvider

logger = logging.getLogger(__name__)


@dataclass
class CollectionResult:
    company_id: int
    company_name: str
    fetched: int      # provider가 반환한 총 개수
    saved: int        # 실제 신규 저장된 개수
    skipped: int      # 중복으로 건너뛴 개수


class NewsCollectionService:

    def __init__(self, db: Session, provider: BaseNewsProvider):
        self.db = db
        self.repo = CompanyNewsRepository(db)
        self.provider = provider

    def collect_for_company(
        self,
        company: Company,
        limit: int = 5,
        dry_run: bool = False,
    ) -> CollectionResult:
        """단일 기업에 대해 뉴스를 수집하고 신규 항목을 저장한다."""
        raw_items: list[NewsItem] = self.provider.fetch(company.name, limit=limit)

        saved = 0
        skipped = 0

        for item in raw_items:
            dup_key = make_duplicate_key(item.url, item.title, item.published_at)

            if self.repo.exists(company.id, dup_key):
                skipped += 1
                logger.debug("중복 뉴스 건너뜀: company=%s title=%s", company.name, item.title[:40])
                continue

            if dry_run:
                logger.info(
                    "[DRY-RUN] 저장 생략 – company=%s | %s | %s",
                    company.name,
                    item.published_at.strftime("%Y-%m-%d"),
                    item.title[:60],
                )
                saved += 1  # dry-run에서도 카운트는 올린다 (미리보기용)
                continue

            self.repo.create(
                company_id=company.id,
                title=item.title,
                url=item.url,
                published_at=item.published_at,
                source_name=item.source_name,
                duplicate_key=dup_key,
                summary=item.summary,
                publisher=item.publisher,
            )
            saved += 1
            logger.info(
                "뉴스 저장: company=%s | %s | %s",
                company.name,
                item.published_at.strftime("%Y-%m-%d"),
                item.title[:60],
            )

        if not dry_run:
            self.db.commit()

        return CollectionResult(
            company_id=company.id,
            company_name=company.name,
            fetched=len(raw_items),
            saved=saved,
            skipped=skipped,
        )
