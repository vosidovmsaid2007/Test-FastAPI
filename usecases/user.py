from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions import SHOULDNT_BLOCK_YOURSELF, USER_NOT_FOUND
from db.user import Session, User, UserActions
from dto.user import UserActionLog, UserActionLogFilters, UserActionLogList, UserListOut


async def user_list(db: AsyncSession) -> UserListOut:
    users = await db.scalars(select(User))
    return UserListOut(users=users.all())

async def reblock_user(email: str, db: AsyncSession, s: Session) -> User:
    user  = await db.scalar(select(User).where(User.email==email))
    if user is None:
        raise USER_NOT_FOUND

    if user.email == s.user.email:
        raise SHOULDNT_BLOCK_YOURSELF

    user.is_active = not user.is_active
    await db.flush()
    return user

async def get_user_action_history(db: AsyncSession, flt: UserActionLogFilters) -> UserActionLogList:

    stmt = select(UserActions)

    if flt.users is not None:
        stmt = stmt.where(UserActions.user_id.in_(flt.users))

    if flt.actions is not None:
        stmt = stmt.where(UserActions.action.in_(flt.actions))

    if flt.fd is not None:
        stmt = stmt.where(func.DATE(UserActions.created_at) >= flt.fd)

    if flt.td is not None:
        stmt = stmt.where(func.DATE(UserActions.created_at) <= flt.td)
    stmt = stmt.options(selectinload(UserActions.user)).order_by(UserActions.created_at.desc())

    result = await db.scalars(stmt)
    result_set = result.all()
    total = len(result_set)

    start = (flt.page - 1) * flt.per_page
    stop = start + flt.per_page

    rows = [UserActionLog(email=r.user.email, action=r.action, date=r.created_at) for r in result_set]

    return UserActionLogList(total_count=total, page=flt.page, records=rows[start:stop])
