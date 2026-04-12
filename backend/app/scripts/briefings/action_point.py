"""
action_point 생성 유틸

LLM 없이 규칙 기반으로 취업 준비 맥락의 액션 포인트를 생성한다.

원칙:
- source_type == "news" 인 경우에만 생성 (job/notice는 None 반환)
- 과장된 분석 금지 — 뉴스 내용 자체를 해석하지 않는다
- headline/기업명을 활용한 행동 유도 문장 수준 유지
- 투자·주가 관점 문구 금지
- 취업 준비 맥락의 행동 제안만 허용
"""

import random


# 취업 준비 맥락 템플릿
# {company}: 기업명 플레이스홀더
_TEMPLATES = [
    "{company} 관련 최근 이슈를 자소서·면접 전에 확인해보세요.",
    "{company}의 최근 변화 내용을 면접 대비용으로 정리해보세요.",
    "이 뉴스가 {company} 지원 동기와 연결될 수 있는지 점검해보세요.",
    "{company} 산업 동향을 파악하고 직무 적합성을 어필할 기회로 활용해보세요.",
    "{company} 관련 현안을 숙지하면 면접에서 차별화된 답변을 할 수 있습니다.",
    "이 내용을 바탕으로 {company}에 대한 지원 스토리를 보강해보세요.",
]


def generate_action_point(
    source_type: str,
    company_name: str,
    headline: str,  # noqa: ARG001 — 향후 키워드 분석 확장 대비 파라미터 유지
) -> str | None:
    """
    브리핑 아이템의 action_point를 생성한다.

    Args:
        source_type: "news" | "job" | "notice"
        company_name: 기업명
        headline: 뉴스 헤드라인 (현재는 사용하지 않으나 향후 키워드 추출 확장 대비)

    Returns:
        str: action_point 문자열 (source_type이 news인 경우)
        None: news가 아닌 경우
    """
    if source_type != "news":
        return None

    template = random.choice(_TEMPLATES)
    return template.format(company=company_name)
