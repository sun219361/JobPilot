"""네이버 뉴스 검색 Provider

공식 문서: https://developers.naver.com/docs/serviceapi/search/news/news.md

환경변수:
  NAVER_CLIENT_ID     – 네이버 오픈API 클라이언트 ID
  NAVER_CLIENT_SECRET – 네이버 오픈API 클라이언트 시크릿

API 키가 없거나 요청 실패 시 빈 리스트를 반환한다 (graceful failure).

dry-run 모드:
  collect_news.py --dry-run 실행 시 이 provider가 반환하는 뉴스 목록을
  DB에 저장하지 않고 stdout으로 출력만 한다.
  provider 자체는 dry-run 여부를 알지 못하며 항상 같은 결과를 반환한다.
  (dry-run 제어는 collect_news.py 레벨에서 담당)
"""

import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx

from app.core.config import settings
from app.scripts.news.news_item import NewsItem
from app.scripts.news.providers.base import BaseNewsProvider

logger = logging.getLogger(__name__)

_NAVER_SEARCH_URL = "https://openapi.naver.com/v1/search/news.json"
_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _HTML_TAG_RE.sub("", text).replace("&quot;", '"').replace("&amp;", "&").strip()


def _parse_pub_date(raw: str) -> datetime:
    """RFC 2822 형식 → timezone-aware datetime"""
    try:
        return parsedate_to_datetime(raw)
    except Exception:
        return datetime.now(tz=timezone.utc)


class NaverNewsProvider(BaseNewsProvider):
    """네이버 뉴스 검색 API를 통한 뉴스 수집"""

    @property
    def source_name(self) -> str:
        return "naver_news"

    def fetch(self, company_name: str, limit: int = 5) -> list[NewsItem]:
        client_id = settings.naver_client_id
        client_secret = settings.naver_client_secret

        if not client_id or not client_secret:
            logger.warning(
                "NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 미설정 – 뉴스 수집을 건너뜁니다."
            )
            return []

        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
        }
        params = {
            "query": company_name,
            "display": min(limit, 100),  # API 최대 100
            "sort": "date",              # 최신순
        }

        try:
            resp = httpx.get(
                _NAVER_SEARCH_URL,
                headers=headers,
                params=params,
                timeout=10.0,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error("네이버 API HTTP 오류 (company=%s): %s", company_name, e)
            return []
        except httpx.RequestError as e:
            logger.error("네이버 API 요청 오류 (company=%s): %s", company_name, e)
            return []

        try:
            data = resp.json()
        except Exception as e:
            logger.error("네이버 API 응답 파싱 오류 (company=%s): %s", company_name, e)
            return []

        items: list[NewsItem] = []
        for raw in data.get("items", []):
            title = _strip_html(raw.get("title", ""))
            link = raw.get("originallink") or raw.get("link", "")
            description = _strip_html(raw.get("description", ""))
            pub_date_str = raw.get("pubDate", "")
            publisher = _strip_html(raw.get("source", "") or "")

            if not title or not link:
                continue

            items.append(
                NewsItem(
                    title=title,
                    url=link,
                    published_at=_parse_pub_date(pub_date_str),
                    source_name=self.source_name,
                    summary=description or None,
                    publisher=publisher or None,
                )
            )

        logger.debug("네이버 뉴스 수집 완료 (company=%s, count=%d)", company_name, len(items))
        return items
