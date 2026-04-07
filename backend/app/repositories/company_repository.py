from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.company import Company, CompanyType
from app.models.prep_snapshot import PrepSnapshot


class CompanyRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_list(
        self,
        q: str | None = None,
        company_type: CompanyType | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Company], int]:
        """기업 목록 조회 + 총 개수 반환"""
        stmt = select(Company).where(Company.is_active == True)  # noqa: E712

        if q:
            stmt = stmt.where(Company.name.ilike(f"%{q}%"))
        if company_type:
            stmt = stmt.where(Company.company_type == company_type)

        # 총 개수
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total: int = self.db.scalar(count_stmt) or 0

        # 페이지네이션
        stmt = stmt.order_by(Company.name).offset(offset).limit(limit)
        companies = list(self.db.scalars(stmt).all())

        return companies, total

    def get_by_id(self, company_id: int) -> Company | None:
        return self.db.get(Company, company_id)

    def get_latest_prep_snapshot(self, company_id: int) -> PrepSnapshot | None:
        stmt = (
            select(PrepSnapshot)
            .where(PrepSnapshot.company_id == company_id)
            .order_by(PrepSnapshot.generated_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
