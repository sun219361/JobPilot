"""users 라우터 – GET /api/v1/users/me

현재 인증된 사용자의 프로필 정보를 반환한다.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.domains.auth.schemas import UserMeResponse
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    summary="내 프로필 조회",
    response_model=None,
)
def get_me(current_user: User = Depends(get_current_user)):
    """Bearer 토큰으로 인증된 현재 사용자의 정보를 반환한다."""
    data = UserMeResponse.model_validate(current_user)
    return success_response(data=data.model_dump())
