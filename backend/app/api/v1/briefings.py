from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.models.user import User
from app.services.briefing_service import BriefingService


router = APIRouter(prefix="/briefings", tags=["briefings"])


@router.get("/today")
def get_today_briefing(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    오늘 브리핑 조회.

    Response:
    - 브리핑 없음: { "success": true, "data": { "briefing": null, "items": [] }, "error": null }
    - 브리핑 있음: { "success": true, "data": { "briefing": {...}, "items": [...sorted by sort_order...] }, "error": null }

    Notes:
    - briefing_date 는 서버 로컬 날짜(date.today()) 기준
    - items 는 sort_order 오름차순 정렬
    - 브리핑 생성은 배치 스크립트(generate_today_briefings.py)가 담당
    """
    service = BriefingService(db)
    result = service.get_today_briefing(current_user)
    return success_response(result.model_dump())
