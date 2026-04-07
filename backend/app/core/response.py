"""
response.py

모든 API 응답의 공통 포맷을 정의한다.

성공: { "success": true, "data": ..., "error": null }
실패: { "success": false, "data": null, "error": { "code": "...", "message": "..." } }
목록: data 안에 items + pagination
"""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel


T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: ErrorDetail | None = None


class PaginationMeta(BaseModel):
    limit: int
    offset: int
    total: int


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    pagination: PaginationMeta


# ── 팩토리 함수 ──────────────────────────────────────

def success_response(data: Any) -> dict:
    return {"success": True, "data": data, "error": None}


def error_response(code: str, message: str) -> dict:
    return {"success": False, "data": None, "error": {"code": code, "message": message}}


def paginated_response(items: list[Any], total: int, limit: int, offset: int) -> dict:
    return {
        "success": True,
        "data": {
            "items": items,
            "pagination": {"limit": limit, "offset": offset, "total": total},
        },
        "error": None,
    }
