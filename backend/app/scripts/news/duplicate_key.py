"""
duplicate_key 생성 유틸

규칙:
  1. URL이 있으면 URL을 정규화한 뒤 SHA-256 앞 16자 hex (32 chars)
  2. URL이 없거나 너무 짧으면 "title|YYYY-MM-DD" 기준 SHA-256 앞 16자 hex

반환값은 32자 hex string → DB의 String(64) 컬럼에 저장.
"""

import hashlib
import re
from datetime import datetime


def _normalize_url(url: str) -> str:
    """쿼리스트링 트래킹 파라미터 제거, 소문자화"""
    # utm_*, fbclid 등 트래킹 파라미터 제거
    url = re.sub(r"[?&](utm_[^&]*|fbclid=[^&]*|gclid=[^&]*)", "", url)
    url = url.rstrip("?&")
    return url.lower().strip()


def make_duplicate_key(
    url: str | None,
    title: str,
    published_at: datetime | None = None,
) -> str:
    if url and len(url) > 10:
        raw = _normalize_url(url)
    else:
        date_str = published_at.strftime("%Y-%m-%d") if published_at else "unknown"
        raw = f"{title.strip()}|{date_str}"

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]
