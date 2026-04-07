from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.briefing import Briefing, BriefingItem


class BriefingRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_today_by_user(self, user_id: int, today: date) -> Briefing | None:
        stmt = (
            select(Briefing)
            .where(
                Briefing.user_id == user_id,
                Briefing.briefing_date == today,
            )
            .options(
                joinedload(Briefing.items).joinedload(BriefingItem.company)
            )
        )
        return self.db.scalar(stmt)
