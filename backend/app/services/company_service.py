from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.company import CompanyType
from app.repositories.company_repository import CompanyRepository
from app.schemas.company import CompanyListItem, CompanyDetail, PrepSnapshotSchema


class CompanyService:

    def __init__(self, db: Session):
        self.repo = CompanyRepository(db)

    def get_company_list(
        self,
        q: str | None,
        company_type: CompanyType | None,
        limit: int,
        offset: int,
    ) -> tuple[list[CompanyListItem], int]:
        companies, total = self.repo.get_list(q=q, company_type=company_type, limit=limit, offset=offset)
        return [CompanyListItem.model_validate(c) for c in companies], total

    def get_company_detail(self, company_id: int) -> CompanyDetail | None:
        company = self.repo.get_by_id(company_id)
        if not company:
            return None

        snapshot = self.repo.get_latest_prep_snapshot(company_id)

        detail = CompanyDetail.model_validate(company)
        detail.latest_prep_snapshot = (
            PrepSnapshotSchema.model_validate(snapshot) if snapshot else None
        )
        return detail
