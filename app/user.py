from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.user import Session, create_user, confirm_email
from dto.user import (
    UserCreateRequest
)
from utils.middlewares import CheckAuth, get_db_session

router = APIRouter(tags=["Admin"], prefix="/users")

db = Annotated[AsyncSession, Depends(get_db_session)]
auth = Annotated[Session, Depends(CheckAuth())]
auth_admin = Annotated[Session, Depends(CheckAuth("admin"))]

@router.post("/add")
async def create_user_request(r: UserCreateRequest, db: db, _: auth):
    return await create_user(db, r)

@router.get("/verify")
async def verify_user(token: str, db: db):
    return await confirm_email(db, token)