from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.models.subscription import Subscription


class SubscriptionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_list_by_user(self, user_id: int) -> list[Subscription]:
        stmt = (
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .options(joinedload(Subscription.company))
            .order_by(Subscription.created_at.desc())
        )
        return list(self.db.scalars(stmt).unique().all())

    def count_by_user(self, user_id: int) -> int:
        stmt = select(func.count()).where(Subscription.user_id == user_id)
        return self.db.scalar(stmt) or 0

    def get_by_id(self, subscription_id: int) -> Subscription | None:
        return self.db.get(Subscription, subscription_id)

    def exists(self, user_id: int, company_id: int) -> bool:
        stmt = select(func.count()).where(
            Subscription.user_id == user_id,
            Subscription.company_id == company_id,
        )
        return (self.db.scalar(stmt) or 0) > 0

    def create(self, user_id: int, company_id: int, memo: str | None) -> Subscription:
        sub = Subscription(user_id=user_id, company_id=company_id, memo=memo)
        self.db.add(sub)
        self.db.flush()
        self.db.refresh(sub)
        return sub

    def delete(self, subscription: Subscription) -> None:
        self.db.delete(subscription)
        self.db.flush()
