from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.repositories.company_repository import CompanyRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.subscription import SubscriptionCreate, SubscriptionItem


class SubscriptionService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = SubscriptionRepository(db)
        self.company_repo = CompanyRepository(db)

    def get_subscriptions(self, current_user: User) -> list[SubscriptionItem]:
        subs = self.repo.get_list_by_user(current_user.id)
        return [SubscriptionItem.model_validate(s) for s in subs]

    def create_subscription(
        self, body: SubscriptionCreate, current_user: User
    ) -> SubscriptionItem:
        # 기업 존재 여부 확인
        company = self.company_repo.get_by_id(body.company_id)
        if not company or not company.is_active:
            raise HTTPException(status_code=404, detail={
                "code": "COMPANY_NOT_FOUND",
                "message": "해당 기업을 찾을 수 없습니다.",
            })

        # 중복 확인
        if self.repo.exists(current_user.id, body.company_id):
            raise HTTPException(status_code=409, detail={
                "code": "DUPLICATE_SUBSCRIPTION",
                "message": "이미 등록된 관심기업입니다.",
            })

        # 한도 확인 (설정값 기반, 하드코딩 금지)
        current_count = self.repo.count_by_user(current_user.id)
        limit = settings.subscription_limit
        if current_count >= limit:
            raise HTTPException(status_code=422, detail={
                "code": "SUBSCRIPTION_LIMIT_EXCEEDED",
                "message": f"관심기업은 최대 {limit}개까지 등록할 수 있습니다.",
                "limit": limit,
                "current": current_count,
            })

        sub = self.repo.create(current_user.id, body.company_id, body.memo)
        self.db.commit()
        self.db.refresh(sub)

        # company 로드
        from sqlalchemy.orm import joinedload
        from sqlalchemy import select
        from app.models.subscription import Subscription
        sub_with_company = self.db.scalar(
            select(Subscription)
            .where(Subscription.id == sub.id)
            .options(joinedload(Subscription.company))
        )
        return SubscriptionItem.model_validate(sub_with_company)

    def delete_subscription(self, subscription_id: int, current_user: User) -> None:
        sub = self.repo.get_by_id(subscription_id)
        if not sub:
            raise HTTPException(status_code=404, detail={
                "code": "SUBSCRIPTION_NOT_FOUND",
                "message": "해당 관심기업을 찾을 수 없습니다.",
            })
        if sub.user_id != current_user.id:
            raise HTTPException(status_code=403, detail={
                "code": "FORBIDDEN",
                "message": "삭제 권한이 없습니다.",
            })
        self.repo.delete(sub)
        self.db.commit()
