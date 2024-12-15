from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from dto.static_types import Role


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Username")
    password: str = Field(..., description="Пароль", min_length=3)


class TokenResponse(BaseModel):
    token: str = Field(..., description="JWT токен для авторизации")
