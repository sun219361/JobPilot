"""auth 도메인 Pydantic 스키마

API 요청/응답 DTO 정의:
- SignupRequest  : 회원가입 요청 (email, password, nickname)
- LoginRequest   : 로그인 요청 (email, password)
- TokenResponse  : 로그인 성공 응답 (access_token, token_type)
- UserMeResponse : /users/me 응답 (id, email, nickname, is_active)
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="최소 8자 이상 비밀번호")
    nickname: str = Field(..., min_length=1, max_length=100)

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMeResponse(BaseModel):
    id: int
    email: str
    nickname: str
    is_active: bool

    model_config = {"from_attributes": True}
