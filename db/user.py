from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.exceptions import HTTPException
import jwt
import bcrypt
from sqlalchemy import ForeignKey, and_, insert, select, update
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import mapped_column, relationship, selectinload
from sqlalchemy.types import UUID, BigInteger, Boolean, DateTime, Enum, String

from core.exceptions import (
    ONLY_ROOT_CAN_MAKE_ITSELF,
    PASSWORDS_DONT_MATCH,
    USER_NOT_FOUND,
    USER_ALREADY_EXISTS,
    TOKEN_NOT_FOUND
)
from db.base import BaseDBModel
from dto.static_types import Role, UserActions
from dto.user import UserCreateRequest
from services.otp import EmailOTPService

EmailOTPService = EmailOTPService()

class JWT:
    SECRET = "a3f78356482b3b5b7950bd9afed2c245"
    ALGORITHM = "HS256"
    EXPIRY = 86400  # seconds (86400)

class User(AsyncAttrs, BaseDBModel):
    __tablename__ = "users"

    id = mapped_column(BigInteger, primary_key=True)
    email = mapped_column(String(100), unique=True)
    password = mapped_column(String(255))
    name = mapped_column(String(255), nullable=True)
    surname = mapped_column(String(255), nullable=True)
    role = mapped_column(Enum(Role), default=Role.user)
    is_active = mapped_column(Boolean, default=True)
    is_confirmed = mapped_column(Boolean, default=False)
    confirmation_token = mapped_column(String(255), nullable=True)

    async def is_password_correct(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    @staticmethod
    async def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(10)).decode("utf-8")

async def get_user_or_none(session: AsyncSession, email: str) -> User:
    return await session.scalar(select(User).where(and_(User.email==email.lower(), User.is_active)))

async def user_make_all_sessions_inactive(session: AsyncSession, user_id: int) -> None:
    return await session.execute(update(Session).values({"is_active": False}).where(Session.user_id==user_id))

def default_otp_expires_in() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=2)

def session_expires_at_default() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=8)

class Session(AsyncAttrs, BaseDBModel):
    __tablename__ = "sessions"

    id = mapped_column(UUID, primary_key=True)
    user_id = mapped_column(BigInteger, ForeignKey("users.id"))

    expires_at = mapped_column(DateTime(timezone=True), default=session_expires_at_default)
    is_active = mapped_column(Boolean, default=True)

    user = relationship(User)

    def is_active_and_not_expired(self) -> bool:
        return self.is_active and datetime.now(timezone.utc) < self.expires_at

async def get_session_by_id(session: AsyncSession, session_id: int) -> Session:
    s = await session.scalar(select(Session).where(Session.id==session_id).options(selectinload(Session.user)))
    if not s.user.is_active:
        return None
    return s


async def send_otp(email: str, token: str) -> None:
    return await EmailOTPService.send_otp(recipient=email, token=token)

async def create_user(s: AsyncSession, r: UserCreateRequest) -> User:
    existing_user = await s.scalar(select(User).where(User.email == r.email.lower()))
    if existing_user:
        raise USER_ALREADY_EXISTS
    
    if r.password != r.password1:
        raise PASSWORDS_DONT_MATCH

    token = jwt.encode(
        {"email": r.email, "exp": datetime.utcnow() + timedelta(hours=1)},
        JWT.SECRET,
        algorithm=JWT.ALGORITHM
    )

    confirm_email = await send_otp(r.email, token)
    if not confirm_email:
        raise USER_ALREADY_EXISTS
    try:
        create_new_user =await s.scalar(insert(User).values({"email": r.email.lower(),
                                               "name": r.name,
                                               "surname": r.surname,
                                               "password": await User.hash_password(r.password),
                                               "role": r.role,
                                               "confirmation_token": token}).returning(User))
        return {"email": create_new_user.email, "is_confirmed": create_new_user.is_confirmed, "is_active": create_new_user.is_active}
    except:
        return {"email": None, "is_confirmed": False, "is_active": False}

async def confirm_email(s: AsyncSession, token: str) -> User:
    try:
        email = jwt.decode(token, JWT.SECRET, algorithms=[JWT.ALGORITHM])
        if not email.get("email"):
            raise USER_NOT_FOUND


        user = await s.scalar(select(User).where(User.email == email.get("email")))
        user.is_confirmed = True
        user.confirmation_token = None
        s.add(user)
        await s.commit()
    except:
        raise TOKEN_NOT_FOUND

    return {"email": email.get("email"), "is_confirmed": user.is_confirmed, "is_active": user.is_active}
    

async def check_is_confirmed(s: AsyncSession, email: str) -> None:
    user = await s.scalar(select(User).where(User.email == email))
    if not user.is_confirmed:
        raise HTTPException(status_code=401, detail="Email is not confirmed!")
    return user

class UserActions(AsyncAttrs, BaseDBModel):
    __tablename__ = "user_actions"

    id = mapped_column(BigInteger, primary_key=True)
    user_id = mapped_column(BigInteger, ForeignKey("users.id"))
    action = mapped_column(Enum(UserActions))

    user = relationship("User")

async def log_an_action(s: AsyncSession, u: User, a: UserActions) -> None:
    await s.execute(insert(UserActions).values({"user_id": u.id, "action": a}))
