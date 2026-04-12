from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.briefing import Briefing, BriefingItem


class BriefingRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_today_by_user(self, user_id: int, today: date) -> Briefing | None:
        """
        오늘 날짜의 브리핑을 조회한다.
        items는 sort_order 오름차순으로 정렬해 반환한다.
        company 관계도 함께 로드해 N+1 쿼리 방지.
        """
        stmt = (
            select(Briefing)
            .where(
                Briefing.user_id == user_id,
                Briefing.briefing_date == today,
            )
            .options(
                joinedload(Briefing.items.and_(True))
                .joinedload(BriefingItem.company)
            )
        )
        briefing = self.db.scalar(stmt)

        if briefing:
            # sort_order 기준 명시적 정렬 (모델의 order_by는 lazy load 시 무시될 수 있음)
            briefing.items.sort(key=lambda item: item.sort_order)

        return briefing
