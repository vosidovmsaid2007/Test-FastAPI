from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    INVALID_PASSWORD,
    USER_NOT_FOUND,
    make_schemas,
)
from db.user import Session, get_user_or_none
from dto.auth import (
    LoginRequest,
    TokenResponse,
)
from dto.user import UserOut
from usecases.auth import login_usecase, validate_token
from utils.middlewares import CheckAuth, get_db_session

router = APIRouter(tags=["Authentication"])

db = Annotated[AsyncSession, Depends(get_db_session)]
auth = Annotated[Session, Depends(CheckAuth())]

@router.post("/login", response_model=TokenResponse,
             responses=make_schemas(INVALID_PASSWORD, USER_NOT_FOUND))
async def login(req: LoginRequest, db_session: db) -> TokenResponse:
    user = await get_user_or_none(db_session, req.email.lower())
    if not user:
        raise USER_NOT_FOUND

    if not await user.is_password_correct(req.password):
        raise INVALID_PASSWORD

    return await login_usecase(db_session, req.email.lower())

@router.get("/validate_token", response_model=UserOut)
async def validate_token_request(user_session: auth) -> UserOut:
    return await validate_token(user_session)
