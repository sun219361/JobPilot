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
    브리핑 없음: { "briefing": null, "items": [] }
    브리핑 있음: { "briefing": {...}, "items": [...] }
    """
    service = BriefingService(db)
    result = service.get_today_briefing(current_user)
    return success_response(result.model_dump())
