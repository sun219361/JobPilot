from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.company import CompanyListItem


class SubscriptionCreate(BaseModel):
    company_id: int
    memo: str | None = None


class SubscriptionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: CompanyListItem
    memo: str | None
    created_at: datetime
