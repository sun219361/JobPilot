"""사람인(Saramin) 채용공고 수집 Provider

공식 API 문서: https://oapi.saramin.co.kr/guide/index

환경변수:
  SARAMIN_API_KEY – 사람인 오픈API 인증키
  (발급: https://oapi.saramin.co.kr/ → 회원가입 → API 키 신청)

API 키가 없거나 요청 실패 시 빈 리스트를 반환한다 (graceful failure).

Provider 선택 이유 (왜 사람인을 1순위로?):
  1. 공개 REST API 제공 – 스크래핑 없이 합법적 수집 가능
  2. 한국 기업 채용공고 커버리지 최상위권
  3. keyword / industry / company_nm 기준 검색 지원
  4. 응답에 직무분류, 경력, 위치, 마감일 등 구조화 데이터 포함
  5. 사람인 API는 무료 플랜에서도 기업명 검색 가능

커버리지 한계 및 fallback 전략:
  - 일부 대기업(삼성, LG 등)은 자체 채용 사이트만 운영해 사람인에 없을 수 있음
  - 이 경우 wanted_provider.py (Wanted API) 또는 공기업용
    public_jobs_provider.py (고용24 API)를 추가해 체인으로 연결 가능.
  - 현재 MVP에서는 사람인 단독. 공고 수가 0이면 warn 로그만 기록.

dry-run 모드:
  collect_jobs.py --dry-run 실행 시 이 provider가 반환하는 결과를
  DB에 저장하지 않고 stdout으로 출력만 한다.
  provider 자체는 dry-run 여부를 알지 못하며 항상 같은 결과를 반환한다.

API 응답 구조 (주요 필드):
  jobs.job[].position.title         → 공고 제목
  jobs.job[].position.industry      → 산업
  jobs.job[].position.job-type      → 고용형태
  jobs.job[].position.work-type     → 근무형태
  jobs.job[].position.location      → 근무지역
  jobs.job[].position.required-years → 경력
  jobs.job[].url                    → 공고 URL
  jobs.job[].posting-date           → 게시일 (Unix timestamp)
  jobs.job[].expiration-date        → 마감일 (Unix timestamp)
"""

import logging
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.scripts.jobs.job_posting_item import JobPostingItem
from app.scripts.jobs.providers.base import BaseJobProvider

logger = logging.getLogger(__name__)

_SARAMIN_API_URL = "https://oapi.saramin.co.kr/job-search"


def _ts_to_dt(ts: str | int | None) -> datetime | None:
    """Unix timestamp(str/int) → timezone-aware datetime. 실패 시 None."""
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except (ValueError, OSError):
        return None


def _extract_text(node: dict | str | None, key: str = "#text") -> str | None:
    """사람인 API는 일부 필드를 {"@id": ..., "#text": "..."} 형태로 반환."""
    if node is None:
        return None
    if isinstance(node, str):
        return node.strip() or None
    return node.get(key, "").strip() or None


class SaraminProvider(BaseJobProvider):
    """사람인 오픈API를 통한 채용공고 수집."""

    @property
    def source_name(self) -> str:
        return "saramin"

    def fetch(self, company_name: str, limit: int = 5) -> list[JobPostingItem]:
        api_key = settings.saramin_api_key

        if not api_key:
            logger.warning(
                "SARAMIN_API_KEY 미설정 – 채용공고 수집을 건너뜁니다. (company=%s)",
                company_name,
            )
            return []

        params = {
            "access-key":    api_key,
            "keywords":      company_name,   # 기업명으로 검색
            "job_mid_cd":    "",             # 직종 전체
            "count":         min(limit, 110),  # API 최대 110
            "sort":          "pd",           # 게시일 최신순
            "fields":        "expiration-date,posting-date,count",
        }

        try:
            resp = httpx.get(_SARAMIN_API_URL, params=params, timeout=15.0)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(
                "사람인 API HTTP 오류 (company=%s status=%s): %s",
                company_name, e.response.status_code, e,
            )
            return []
        except httpx.RequestError as e:
            logger.error("사람인 API 요청 오류 (company=%s): %s", company_name, e)
            return []

        try:
            data = resp.json()
        except Exception as e:
            logger.error("사람인 API 응답 파싱 오류 (company=%s): %s", company_name, e)
            return []

        raw_jobs = data.get("jobs", {}).get("job", [])
        if not isinstance(raw_jobs, list):
            raw_jobs = [raw_jobs] if raw_jobs else []

        items: list[JobPostingItem] = []
        for job in raw_jobs:
            try:
                item = self._parse_job(job)
                if item:
                    items.append(item)
            except Exception as e:
                logger.warning("공고 파싱 오류: %s – %s", e, job)
                continue

        logger.debug(
            "사람인 수집 완료 (company=%s, count=%d)", company_name, len(items)
        )
        return items

    def _parse_job(self, job: dict) -> JobPostingItem | None:
        """단일 job 노드를 JobPostingItem으로 변환."""
        position = job.get("position", {})
        company_info = job.get("company", {}).get("detail", {})

        title = _extract_text(position.get("title"))
        if not title:
            return None

        url = job.get("url", "")
        if not url:
            return None

        # 고용형태
        job_type_node = position.get("job-type", {})
        employment_type = _extract_text(job_type_node)

        # 근무지역
        loc_node = position.get("location", {})
        location = _extract_text(loc_node)

        # 직무분류 (department로 활용)
        job_category = position.get("job-category", {})
        department = _extract_text(job_category)

        # 날짜
        posted_at   = _ts_to_dt(job.get("posting-date"))
        deadline_at = _ts_to_dt(job.get("expiration-date"))

        return JobPostingItem(
            title=title,
            posting_url=url,
            source_name=self.source_name,
            department=department,
            employment_type=employment_type,
            location=location,
            # 사람인 기본 API는 상세 텍스트(responsibilities 등)를 제공하지 않음.
            # 상세 엔드포인트 호출이 필요하지만 MVP에서는 생략.
            responsibilities=None,
            qualifications=None,
            preferred=None,
            posted_at=posted_at,
            deadline_at=deadline_at,
        )
