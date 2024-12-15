from __future__ import annotations

from typing import Literal

import jwt
from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.user import JWT, Session, get_session_by_id
from core.config import DBInstance
from core.exceptions import NOT_AUTHENTICATED
from dto.static_types import Role
from db.user import check_is_confirmed

bearer = HTTPBearer(description="Используйте JWT access_token для аутентификации")

class CheckAuth:

    def __init__(self, check_type: Literal["admin"] | None = None) -> None:
        self.type = check_type

    async def __call__(self, token: HTTPAuthorizationCredentials = Depends(bearer)) -> Session:
        try:
            payload = jwt.decode(token.credentials, JWT.SECRET, algorithms=[JWT.ALGORITHM])
            session_id = payload.get("session_id")
            if session_id is None:
                raise NOT_AUTHENTICATED
            async with DBInstance.SESSION_MAKER() as s:
                session = await get_session_by_id(s, session_id)
                if session.user.role != Role.admin:
                    await check_is_confirmed(s, session.user.email)
                    
                if not session:
                    raise NOT_AUTHENTICATED
                if not session.is_active_and_not_expired():
                    raise NOT_AUTHENTICATED
                if self.type is not None and session.user.role not in [Role.root, Role.admin]:
                    raise NOT_AUTHENTICATED
                return session
        except jwt.PyJWTError as exc:
            raise NOT_AUTHENTICATED from exc


async def get_db_session():
    session = DBInstance.SESSION_MAKER()
    try:
        yield session
    except Exception as exc:
        await session.rollback()
        raise exc
    finally:
        await session.commit()
        await session.close()
