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


@router.get("/{company_id}/news")
def get_company_news(
    company_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """기업별 최신 뉴스 목록 (published_at 기준 내림차순)"""
    service = CompanyService(db)
    detail = service.get_company_detail(company_id)
    if not detail:
        return error_response("COMPANY_NOT_FOUND", "해당 기업을 찾을 수 없습니다.")

    items, total = service.get_company_news(company_id, limit=limit, offset=offset)
    return paginated_response(
        items=[item.model_dump() for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{company_id}/jobs")
def get_company_jobs(
    company_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """기업별 채용공고 목록 (OPEN 우선, 게시일 최신순).

    Response:
    - OPEN 공고 → UNKNOWN 공고 → CLOSED 공고 순 정렬
    - 동일 status 내에서는 posted_at 내림차순
    - status: OPEN | CLOSED | UNKNOWN
    - keywords: rule-based 추출 키워드 목록 (없으면 null)
    """
    service = CompanyService(db)
    detail = service.get_company_detail(company_id)
    if not detail:
        return error_response("COMPANY_NOT_FOUND", "해당 기업을 찾을 수 없습니다.")

    items, total = service.get_company_jobs(company_id, limit=limit, offset=offset)
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
    """기업 상세 조회 (최신 prep snapshot 포함).

    설계 결정 – 채용공고 preview 미포함:
    - 뉴스와 달리 채용공고는 TTL이 짧고 OPEN/CLOSED 상태가 수시로 변함.
    - 기업 상세 응답에 공고 preview를 포함하면 캐싱 전략이 복잡해짐.
    - GET /api/v1/companies/{id}/jobs 를 별도로 호출하는 방식이
      클라이언트 선택적 로딩(lazy load)에 적합함.
    - 향후 UX 개선이 필요하면 `include_jobs=true` 쿼리 파라미터로
      선택적으로 preview를 포함할 수 있다.
    """
    service = CompanyService(db)
    detail = service.get_company_detail(company_id)
    if not detail:
        return error_response("COMPANY_NOT_FOUND", "해당 기업을 찾을 수 없습니다.")
    return success_response(detail.model_dump())
