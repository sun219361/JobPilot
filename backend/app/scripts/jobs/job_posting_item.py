"""
JobPostingItem DTO – 채용공고 provider가 반환하는 공통 데이터 클래스

모든 provider는 이 형식으로 결과를 반환한다.
duplicate_key는 수집 파이프라인에서 별도 유틸로 계산 후 주입한다.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class JobPostingItem:
    # 필수
    title: str
    posting_url: str
    source_name: str              # provider 식별자 (예: "saramin")

    # 선택 – provider별 제공 여부 다름
    department: str | None = None
    employment_type: str | None = None   # 정규직 / 계약직 / 인턴
    location: str | None = None
    responsibilities: str | None = None
    qualifications: str | None = None
    preferred: str | None = None
    posted_at: datetime | None = None
    deadline_at: datetime | None = None

    # 수집 파이프라인에서 주입
    duplicate_key: str = field(default="")
