"""
duplicate_key.py – 채용공고 중복 방지 키 생성 유틸

규칙 (우선순위 순):
  1. posting_url이 유효하면 → URL 정규화 후 SHA-256 앞 32자 hex
  2. URL이 없거나 짧으면   → "title|source_name|YYYY-MM-DD" hash
     posted_at 도 없으면   → "title|source_name" hash

반환값: 32자 hex string (DB String(64) 컬럼에 저장)

설계 이유:
  - 채용공고 URL은 대체로 공고 식별자를 포함하므로 URL hash가 가장 안정적.
  - 일부 사람인 공고는 URL 파라미터가 변경될 수 있으므로 트래킹 파라미터 제거.
  - URL이 없는 경우(스크래핑 실패 등) title+source+날짜 조합으로 fallback.
  - CompanyNews의 make_duplicate_key와 동일한 전략을 의도적으로 따른다.
    → 코드베이스 일관성 유지. 향후 공통 유틸로 합칠 수 있다.
"""

import hashlib
import re
from datetime import datetime


def _normalize_url(url: str) -> str:
    """트래킹 파라미터 제거, scheme+host+path만 남겨 소문자화."""
    # utm_*, fbclid, gclid 등 제거
    url = re.sub(r"[?&](utm_[^&]*|fbclid=[^&]*|gclid=[^&]*)", "", url)
    # 사람인 특유의 sr_no 같은 내부 파라미터는 유지 (공고 식별에 사용됨)
    url = url.rstrip("?&")
    return url.lower().strip()


def make_job_duplicate_key(
    posting_url: str | None,
    title: str,
    source_name: str,
    posted_at: datetime | None = None,
) -> str:
    """
    채용공고 duplicate_key를 생성한다.

    Args:
        posting_url: 공고 원본 URL (없으면 None)
        title:       공고 제목
        source_name: provider 식별자 (예: "saramin")
        posted_at:   게시일 (없으면 날짜 부분 생략)

    Returns:
        32자 hex string
    """
    if posting_url and len(posting_url) > 10:
        raw = _normalize_url(posting_url)
    else:
        date_str = posted_at.strftime("%Y-%m-%d") if posted_at else ""
        parts = [title.strip(), source_name, date_str]
        raw = "|".join(p for p in parts if p)

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
