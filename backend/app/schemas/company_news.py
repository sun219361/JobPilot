"""company_news Pydantic 응답 스키마"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CompanyNewsItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str | None
    publisher: str | None
    published_at: datetime
    url: str
    source_name: str
