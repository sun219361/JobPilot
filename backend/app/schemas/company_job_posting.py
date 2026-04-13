"""company_job_posting Pydantic 응답 스키마"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.company_job_posting import PostingStatus


class CompanyJobPostingItem(BaseModel):
    """GET /api/v1/companies/{id}/jobs 응답 항목."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    department: Optional[str]
    employment_type: Optional[str]
    location: Optional[str]
    status: PostingStatus
    posting_url: str
    source_name: str
    posted_at: Optional[datetime]
    deadline_at: Optional[datetime]
    keywords: Optional[list[str]]
