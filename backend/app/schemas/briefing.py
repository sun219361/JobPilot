from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class BriefingItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_id: int | None
    company_name: str | None  # 조인 후 service 레이어에서 채움
    source_type: str
    headline: str
    summary: str
    action_point: str | None
    sort_order: int


class BriefingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    briefing_date: date
    title: str
    created_at: datetime
    items: list[BriefingItemSchema]


class TodayBriefingResponse(BaseModel):
    """
    /briefings/today 전용 응답.
    브리핑이 없으면 briefing=None, items=[]
    """

    briefing: BriefingSchema | None
    items: list[BriefingItemSchema]
