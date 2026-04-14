from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.models.company import CompanyType


class PrepSnapshotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    one_line_summary: str
    recent_issue_summary: str
    hiring_summary: str
    talent_summary: str
    cover_letter_points: list[str]
    interview_points: list[str]
    generation_date: Optional[date] = None   # 생성 기준 날짜 (Phase 4 추가)
    source_version: Optional[str] = None     # "auto_batch" | "seed" | "manual"
    generated_at: datetime


class CompanyListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    company_type: CompanyType
    industry: str
    summary: str
    is_active: bool


class CompanyDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    company_type: CompanyType
    industry: str
    summary: str
    homepage_url: str | None
    careers_url: str | None
    is_active: bool
    latest_prep_snapshot: PrepSnapshotSchema | None = None
