from datetime import date

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.briefing_repository import BriefingRepository
from app.schemas.briefing import TodayBriefingResponse, BriefingSchema, BriefingItemSchema


class BriefingService:

    def __init__(self, db: Session):
        self.repo = BriefingRepository(db)

    def get_today_briefing(self, current_user: User) -> TodayBriefingResponse:
        today = date.today()
        briefing = self.repo.get_today_by_user(current_user.id, today)

        if not briefing:
            return TodayBriefingResponse(briefing=None, items=[])

        items = [
            BriefingItemSchema(
                id=item.id,
                company_id=item.company_id,
                company_name=item.company.name if item.company else None,
                source_type=item.source_type,
                headline=item.headline,
                summary=item.summary,
                action_point=item.action_point,
                sort_order=item.sort_order,
            )
            for item in sorted(briefing.items, key=lambda x: x.sort_order)
        ]

        briefing_schema = BriefingSchema(
            id=briefing.id,
            briefing_date=briefing.briefing_date,
            title=briefing.title,
            created_at=briefing.created_at,
            items=items,
        )

        return TodayBriefingResponse(briefing=briefing_schema, items=items)
