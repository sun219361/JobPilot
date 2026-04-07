from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.response import success_response, paginated_response
from app.models.user import User
from app.schemas.subscription import SubscriptionCreate
from app.services.subscription_service import SubscriptionService


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("")
def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """현재 사용자의 관심기업 목록"""
    service = SubscriptionService(db)
    items = service.get_subscriptions(current_user)
    return paginated_response(
        items=[item.model_dump() for item in items],
        total=len(items),
        limit=len(items),
        offset=0,
    )


@router.post("", status_code=201)
def create_subscription(
    body: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """관심기업 등록"""
    service = SubscriptionService(db)
    item = service.create_subscription(body, current_user)
    return success_response(item.model_dump())


@router.delete("/{subscription_id}", status_code=200)
def delete_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """관심기업 삭제"""
    service = SubscriptionService(db)
    service.delete_subscription(subscription_id, current_user)
    return success_response({"deleted": True, "subscription_id": subscription_id})
