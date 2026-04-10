"""
NewsItem DTO – 뉴스 provider가 반환하는 공통 데이터 클래스
모든 provider는 이 형식으로 결과를 반환한다.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NewsItem:
    title: str
    url: str
    published_at: datetime
    source_name: str              # provider 식별자 (예: "naver_news")
    summary: str | None = None
    publisher: str | None = None  # 언론사 이름
    # duplicate_key는 수집 파이프라인에서 utils로 계산 후 주입
    duplicate_key: str = field(default="")
