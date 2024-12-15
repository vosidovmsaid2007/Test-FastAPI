from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.user import JWT
from db.user import (
    Session,
    User,
    get_user_or_none,
    log_an_action,
    user_make_all_sessions_inactive,
)
from dto.auth import TokenResponse
from dto.static_types import UserActions


async def issue_jwt_token(user_id: str) -> str:
    return jwt.encode(
        {
            "exp": datetime.now(timezone.utc) + timedelta(seconds=JWT.EXPIRY),
            "session_id": user_id,
        },
        JWT.SECRET,
    )

async def login_usecase(session: AsyncSession, email: str) -> TokenResponse:
    user = await get_user_or_none(session, email)

    await user_make_all_sessions_inactive(session, user.id)
    u_s = await session.scalar(insert(Session).values({"id": uuid4(), "user_id": user.id}).returning(Session))

    token = await issue_jwt_token(str(u_s.id))
    await log_an_action(session, user, UserActions.logged_in)
    return TokenResponse(token=token)

async def validate_token(s: Session) -> User:
    return s.user
