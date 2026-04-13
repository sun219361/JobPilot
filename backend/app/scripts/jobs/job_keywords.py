"""
job_keywords.py – rule-based 채용공고 키워드 추출 유틸

설계 원칙:
- AI / ML 없음. 미리 정의한 keyword list와 단순 문자열 매칭만 사용.
- 공고 텍스트(title / responsibilities / qualifications / preferred)에서
  대소문자 무관하게 키워드 포함 여부 검사 후 매칭된 키워드 목록 반환.
- 중복 제거, 알파벳 정렬 → DB JSON에 저장.
- 향후 AI 분류가 도입되면 이 유틸만 교체하면 된다.

키워드 카테고리:
  - 언어/기술: Python, SQL, Java, ...
  - 데이터/AI: 데이터분석, 머신러닝, AI, ...
  - 직군: 백엔드, 프론트엔드, DevOps, ...
  - 산업: 금융, 핀테크, 이커머스, ...
  - 소프트스킬: 협업, 커뮤니케이션, ...
"""

from __future__ import annotations

import re

# ── 사전 정의 키워드 목록 ─────────────────────────────────────────
# 각 항목은 (표시명, [검색 패턴 list]) 형태.
# 검색 패턴은 단순 substring 매칭 (re.IGNORECASE).

_KEYWORD_PATTERNS: list[tuple[str, list[str]]] = [
    # 프로그래밍 언어
    ("Python",       ["python", "파이썬"]),
    ("Java",         ["java(?!script)", "자바(?!스크립트)"]),
    ("JavaScript",   ["javascript", "자바스크립트"]),
    ("TypeScript",   ["typescript", "타입스크립트"]),
    ("Kotlin",       ["kotlin", "코틀린"]),
    ("Swift",        ["swift", "스위프트"]),
    ("C++",          [r"c\+\+"]),
    ("Go",           [r"\bgo\b", r"\bgolang\b"]),
    ("Rust",         [r"\brust\b"]),
    # 데이터/인프라
    ("SQL",          [r"\bsql\b", "데이터베이스"]),
    ("NoSQL",        ["nosql", "mongodb", "cassandra", "dynamodb"]),
    ("MySQL",        ["mysql"]),
    ("PostgreSQL",   ["postgresql", "postgres"]),
    ("Redis",        ["redis"]),
    ("Kafka",        ["kafka"]),
    ("Spark",        [r"\bspark\b", "아파치 스파크"]),
    ("Hadoop",       ["hadoop"]),
    # 클라우드/DevOps
    ("AWS",          [r"\baws\b", "amazon web services"]),
    ("GCP",          [r"\bgcp\b", "google cloud"]),
    ("Azure",        [r"\bazure\b"]),
    ("Docker",       ["docker"]),
    ("Kubernetes",   ["kubernetes", r"\bk8s\b"]),
    ("CI/CD",        ["ci/cd", "cicd", "jenkins", "github actions", "gitlab ci"]),
    ("Linux",        ["linux", "리눅스"]),
    # AI/ML
    ("AI",           [r"\bai\b", "인공지능"]),
    ("ML",           [r"\bml\b", "머신러닝", "machine learning"]),
    ("딥러닝",       ["딥러닝", "deep learning"]),
    ("LLM",          [r"\bllm\b", "large language model"]),
    ("데이터분석",   ["데이터 분석", "데이터분석", "data analy"]),
    ("데이터엔지니어링", ["데이터 엔지니어", "데이터엔지니어", "data engineer"]),
    # 웹/백엔드/프론트
    ("백엔드",       ["백엔드", "back-end", "backend", "server-side"]),
    ("프론트엔드",   ["프론트엔드", "front-end", "frontend"]),
    ("React",        [r"\breact\b"]),
    ("Vue",          [r"\bvue\b"]),
    ("Spring",       [r"\bspring\b"]),
    ("FastAPI",      ["fastapi"]),
    ("Django",       ["django"]),
    ("REST API",     ["rest api", "restful", "api 개발"]),
    # 산업
    ("금융",         ["금융", "핀테크", "fintech", "뱅킹", "결제"]),
    ("이커머스",     ["이커머스", "e-commerce", "커머스"]),
    ("게임",         ["게임", "gaming"]),
    ("모빌리티",     ["모빌리티", "mobility", "자율주행"]),
    ("헬스케어",     ["헬스케어", "바이오", "의료"]),
    # 소프트스킬
    ("협업",         ["협업", "collaboration", "팀워크", "teamwork"]),
    ("커뮤니케이션", ["커뮤니케이션", "소통"]),
    ("문제해결",     ["문제 해결", "문제해결", "problem solving"]),
    # 기타 직무 키워드
    ("신입",         ["신입"]),
    ("경력",         ["경력", r"\d+년 이상", r"\d+년 이상의 경험"]),
    ("공채",         ["공채", "공개채용"]),
    ("인턴",         ["인턴"]),
]

# 컴파일된 패턴 캐시 (모듈 임포트 시 1회 컴파일)
_COMPILED: list[tuple[str, list[re.Pattern]]] = [
    (label, [re.compile(p, re.IGNORECASE) for p in patterns])
    for label, patterns in _KEYWORD_PATTERNS
]


def extract_keywords(
    title: str = "",
    responsibilities: str | None = None,
    qualifications: str | None = None,
    preferred: str | None = None,
    extra_keywords: list[str] | None = None,
) -> list[str]:
    """
    공고 텍스트에서 사전 정의 키워드를 추출해 정렬된 목록으로 반환한다.

    Args:
        title:            공고 제목
        responsibilities: 담당업무
        qualifications:   자격요건
        preferred:        우대사항
        extra_keywords:   설정에서 주입하는 추가 키워드 목록 (선택)

    Returns:
        중복 제거된 정렬 키워드 list. 빈 경우 [] 반환.
    """
    # 검색 대상 텍스트 합치기
    combined = " ".join(
        part for part in [title, responsibilities, qualifications, preferred]
        if part
    )
    if not combined.strip():
        return []

    matched: set[str] = set()

    # 사전 패턴 매칭
    for label, patterns in _COMPILED:
        for pattern in patterns:
            if pattern.search(combined):
                matched.add(label)
                break  # 해당 label은 이미 매칭됨

    # 설정에서 주입된 추가 키워드 (단순 substring)
    if extra_keywords:
        for kw in extra_keywords:
            if kw and kw.lower() in combined.lower():
                matched.add(kw)

    return sorted(matched)
