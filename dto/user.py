from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from dto.static_types import Role, UserActions


class UserOut(BaseModel):
    created_at: datetime
    id: int
    email: str
    surname: str | None
    name: str | None
    role: Role
    is_active: bool

    class Config:
        from_attributes = True

class UserListOut(BaseModel):
    users: list[UserOut]

class UserCreateRequest(BaseModel):
    email:EmailStr
    name: str
    surname: str
    password: str
    password1: str
    role: Role

class UserUpdateRequest(BaseModel):
    email: str | None = Field(default=None)
    surname: str | None = Field(default=None)
    name: str | None = Field(default=None)
    password: str | None = Field(default=None)
    password1: str | None = Field(default=None)
    role: Role | None = Field(default=None)

class UserActionLogFilters(BaseModel):
    users: list[int] | None
    actions: list[UserActions] | None
    fd: datetime | None
    td: datetime | None
    page: int = Field(default=1)
    per_page: int = Field(default=15)

class UserActionLog(BaseModel):
    email: str
    action: str
    date: datetime

class UserActionLogList(BaseModel):
    records: list[UserActionLog]
    total_count: int
    page: int
