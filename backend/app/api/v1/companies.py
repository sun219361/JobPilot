from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.response import success_response, error_response, paginated_response
from app.models.company import CompanyType
from app.services.company_service import CompanyService


router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("")
def get_companies(
    q: str | None = Query(default=None, description="기업명 검색"),
    company_type: CompanyType | None = Query(default=None, description="기업 유형 필터"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """기업 목록 조회 (검색 + 필터 + 페이지네이션)"""
    service = CompanyService(db)
    items, total = service.get_company_list(q=q, company_type=company_type, limit=limit, offset=offset)
    return paginated_response(
        items=[item.model_dump() for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{company_id}")
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
):
    """기업 상세 조회 (최신 prep snapshot 포함)"""
    service = CompanyService(db)
    detail = service.get_company_detail(company_id)
    if not detail:
        return error_response("COMPANY_NOT_FOUND", "해당 기업을 찾을 수 없습니다.")
    return success_response(detail.model_dump())
