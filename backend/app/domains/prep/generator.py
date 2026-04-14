"""generator.py – 규칙 기반 PrepSnapshot 필드 생성 유틸

설계 원칙:
- LLM / AI / 감성분석 없음. 순수 rule-based 텍스트 조합.
- 모든 문장은 "정보 정리와 준비 방향" 수준이며 실제 없는 사실을 만들지 않는다.
- 과장된 해석, 투자/주가 관점, 기출 면접 척하기 금지.
- 각 필드에 fallback 규칙이 반드시 존재한다.
- 외부 의존성 없음 (stdlib만 사용).

입력 데이터 타입 (DTO):
- CompanyContext: generator에 전달되는 단순 데이터 컨테이너
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.models.company import CompanyType

logger = logging.getLogger(__name__)


# ── 입력 DTO ──────────────────────────────────────────────────────────────


@dataclass
class NewsItem:
    """뉴스 아이템 요약 DTO (generator용)."""
    title: str
    summary: str | None = None


@dataclass
class JobItem:
    """채용공고 요약 DTO (generator용)."""
    title: str
    department: str | None = None
    employment_type: str | None = None
    keywords: list[str] = field(default_factory=list)


@dataclass
class CompanyContext:
    """snapshot 생성에 필요한 기업 컨텍스트.

    service.py가 DB에서 조회한 데이터를 이 DTO로 변환해 generator에 전달한다.
    generator는 DB 접근 없이 순수 텍스트 생성만 담당한다.
    """
    company_id: int
    name: str
    company_type: CompanyType
    industry: str
    summary: str                       # Company.summary
    recent_news: list[NewsItem] = field(default_factory=list)
    open_jobs: list[JobItem]   = field(default_factory=list)


# ── 출력 DTO ──────────────────────────────────────────────────────────────


@dataclass
class SnapshotFields:
    """generator가 반환하는 snapshot 필드 묶음."""
    one_line_summary: str
    recent_issue_summary: str
    hiring_summary: str
    talent_summary: str
    cover_letter_points: list[str]
    interview_points: list[str]


# ── 내부 헬퍼 ─────────────────────────────────────────────────────────────

# 기업 유형별 준비 방향 키워드 테이블
_TYPE_TALENT_HINT: dict[CompanyType, str] = {
    CompanyType.LARGE:  "글로벌 대기업 환경에 맞는 협업 능력과 직무 전문성",
    CompanyType.MID:    "빠른 성장 환경에서의 자기주도적 역량과 실무 경험",
    CompanyType.PUBLIC: "공공 서비스 이해와 책임감 있는 업무 수행 역량",
}

# 기업 유형별 자소서 기본 포인트
_TYPE_COVER_HINT: dict[CompanyType, list[str]] = {
    CompanyType.LARGE: [
        "지원 기업의 사업 방향성과 본인의 커리어 목표를 연결하여 작성하세요.",
        "글로벌 환경에서의 협업 경험이나 다양성 수용 역량을 구체적으로 제시하세요.",
    ],
    CompanyType.MID: [
        "빠른 환경 변화에 적응한 경험을 중심으로 자기주도성을 강조하세요.",
        "성장 가능성과 함께 즉시 기여 가능한 실무 역량을 구체적으로 표현하세요.",
    ],
    CompanyType.PUBLIC: [
        "공공 서비스의 사회적 가치와 본인의 지원 동기를 연결하여 작성하세요.",
        "규정 준수와 책임감을 바탕으로 한 업무 경험을 구체적으로 기술하세요.",
    ],
}

# 기업 유형별 면접 기본 포인트
_TYPE_INTERVIEW_HINT: dict[CompanyType, list[str]] = {
    CompanyType.LARGE: [
        "기업의 최근 사업 현황과 주요 변화 방향을 미리 파악해 두세요.",
        "지원 직무의 역할 범위와 팀 구조를 사전에 조사하세요.",
    ],
    CompanyType.MID: [
        "기업의 성장 단계와 현재 주력 사업 분야를 파악해 두세요.",
        "빠른 적응력과 문제 해결 사례를 구체적인 수치나 결과 중심으로 정리하세요.",
    ],
    CompanyType.PUBLIC: [
        "해당 기관의 최근 정책 변화나 공공 사업 방향을 파악해 두세요.",
        "공무원/공공기관 직업관과 서비스 마인드를 명확하게 정리해 두세요.",
    ],
}


def _collect_all_keywords(jobs: list[JobItem]) -> list[str]:
    """채용공고 키워드 중복 제거 후 정렬된 목록 반환."""
    seen: set[str] = set()
    result: list[str] = []
    for j in jobs:
        for kw in j.keywords:
            if kw not in seen:
                seen.add(kw)
                result.append(kw)
    return result


# ── 공개 generator 함수 ───────────────────────────────────────────────────


def generate_snapshot_fields(ctx: CompanyContext) -> SnapshotFields:
    """규칙 기반으로 PrepSnapshot 필드를 생성하고 반환한다.

    Args:
        ctx: 기업 컨텍스트 DTO

    Returns:
        SnapshotFields: snapshot에 저장할 필드 값들
    """
    return SnapshotFields(
        one_line_summary     = _build_one_line_summary(ctx),
        recent_issue_summary = _build_recent_issue_summary(ctx),
        hiring_summary       = _build_hiring_summary(ctx),
        talent_summary       = _build_talent_summary(ctx),
        cover_letter_points  = _build_cover_letter_points(ctx),
        interview_points     = _build_interview_points(ctx),
    )


# ── 필드별 생성 함수 ──────────────────────────────────────────────────────


def _build_one_line_summary(ctx: CompanyContext) -> str:
    """[1] one_line_summary

    우선순위:
    1. Company.summary가 있으면 그대로 사용 (최대 120자 truncate)
    2. company_type + industry 기반 fallback 문장
    """
    if ctx.summary and ctx.summary.strip():
        text = ctx.summary.strip()
        return text[:120] + ("…" if len(text) > 120 else "")

    # fallback
    type_label = {
        CompanyType.LARGE:  "대기업",
        CompanyType.MID:    "중견기업",
        CompanyType.PUBLIC: "공공기관",
    }.get(ctx.company_type, "기업")
    return f"{ctx.industry} 분야 {type_label}인 {ctx.name}입니다."


def _build_recent_issue_summary(ctx: CompanyContext) -> str:
    """[2] recent_issue_summary

    규칙:
    - 최근 뉴스가 1건 이상 있으면 제목/요약 기반으로 1~2문장 조합
    - 뉴스가 없으면 fallback 문장
    - 과장 금지, 투자/주가 관점 금지
    """
    if not ctx.recent_news:
        return "최근 수집된 주요 뉴스가 없습니다."

    parts: list[str] = []
    for i, news in enumerate(ctx.recent_news[:2]):  # 최대 2건만 반영
        base = news.title.strip().rstrip(".")
        if news.summary and news.summary.strip():
            # 요약이 있으면 50자 이내로 압축
            snippet = news.summary.strip()[:50].rstrip(".")
            parts.append(f"{base} – {snippet}.")
        else:
            parts.append(f"{base}.")

    intro = f"최근 {ctx.name} 관련 주요 뉴스: "
    body = " ".join(parts)
    return intro + body


def _build_hiring_summary(ctx: CompanyContext) -> str:
    """[3] hiring_summary

    규칙:
    - OPEN 채용공고가 있으면 공고 title / department / employment_type 기반 요약
    - 없으면 fallback 문장
    """
    if not ctx.open_jobs:
        return "현재 수집된 채용공고 정보가 없습니다."

    lines: list[str] = []
    for job in ctx.open_jobs[:3]:  # 최대 3건
        parts = [job.title.strip()]
        details: list[str] = []
        if job.department:
            details.append(job.department)
        if job.employment_type:
            details.append(job.employment_type)
        if details:
            parts.append(f"({', '.join(details)})")
        lines.append(" ".join(parts))

    count = len(ctx.open_jobs)
    count_text = (
        f"현재 {ctx.name}의 공개 채용공고 {count}건이 수집되어 있습니다."
        if count > 0 else "현재 수집된 채용공고 정보가 없습니다."
    )
    postings_text = " | ".join(lines)
    return f"{count_text} 주요 공고: {postings_text}."


def _build_talent_summary(ctx: CompanyContext) -> str:
    """[4] talent_summary

    규칙:
    - 채용공고 키워드 + 기업 유형 + 산업 기반으로 준비 방향 문장 생성
    - 과도한 추론 금지
    """
    type_hint = _TYPE_TALENT_HINT.get(
        ctx.company_type,
        "직무 전문성과 팀 협업 역량"
    )

    keywords = _collect_all_keywords(ctx.open_jobs)
    if keywords:
        kw_text = ", ".join(keywords[:5])  # 최대 5개 키워드
        return (
            f"{ctx.name}은 {ctx.industry} 분야 기업으로, "
            f"최근 채용에서 {kw_text} 등의 역량을 중시하고 있습니다. "
            f"{type_hint}을 중심으로 준비하는 것을 권장합니다."
        )

    # 키워드 없으면 기업유형 기반 fallback
    return (
        f"{ctx.name}은 {ctx.industry} 분야 기업입니다. "
        f"{type_hint}을 중심으로 준비하는 것을 권장합니다."
    )


def _build_cover_letter_points(ctx: CompanyContext) -> list[str]:
    """[5] cover_letter_points

    규칙:
    - 기업 유형 기반 기본 2개 포인트
    - 최근 뉴스가 있으면 최근 이슈 포인트 1개 추가
    - 채용공고 키워드가 있으면 직무 역량 포인트 1개 추가
    - 실제 없는 사실 만들지 않음
    """
    points: list[str] = list(_TYPE_COVER_HINT.get(ctx.company_type, []))

    # 뉴스 기반 포인트
    if ctx.recent_news:
        issue_title = ctx.recent_news[0].title.strip()[:40]
        points.append(
            f"최근 이슈(예: '{issue_title}')를 면접 준비 시 참고하여 "
            f"기업의 현재 방향성을 이해하고 있음을 표현하세요."
        )

    # 채용공고 키워드 기반 포인트
    keywords = _collect_all_keywords(ctx.open_jobs)
    if keywords:
        kw_text = ", ".join(keywords[:3])
        points.append(
            f"공고에서 요구하는 역량({kw_text})과 본인의 경험을 "
            f"구체적인 사례로 연결하여 직무 적합성을 강조하세요."
        )

    return points[:4]  # 최대 4개


def _build_interview_points(ctx: CompanyContext) -> list[str]:
    """[6] interview_points

    규칙:
    - 기업 유형 기반 기본 2개 포인트
    - 최근 뉴스가 있으면 최근 이슈 확인 포인트 1개 추가
    - 채용공고 역량이 있으면 역량 정리 포인트 1개 추가
    - 면접 기출을 아는 것처럼 쓰지 않음
    """
    points: list[str] = list(_TYPE_INTERVIEW_HINT.get(ctx.company_type, []))

    # 뉴스 기반 포인트
    if ctx.recent_news:
        issue_title = ctx.recent_news[0].title.strip()[:40]
        points.append(
            f"최근 주요 이슈('{issue_title}')와 관련된 기업 변화를 "
            f"사전에 파악하고 자신의 의견을 정리해 두세요."
        )

    # 채용공고 역량 기반 포인트
    keywords = _collect_all_keywords(ctx.open_jobs)
    if keywords:
        kw_text = ", ".join(keywords[:3])
        points.append(
            f"공고 요구 역량({kw_text})을 바탕으로 본인의 "
            f"관련 경험과 강점을 사전에 정리해 두세요."
        )

    return points[:4]  # 최대 4개
