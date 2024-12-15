from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from db.user import Session
from usecases.application import products_list
from utils.middlewares import CheckAuth, get_db_session

router = APIRouter(tags=["Products"], prefix="/products")

db = Annotated[AsyncSession, Depends(get_db_session)]
auth = Annotated[Session, Depends(CheckAuth())]
auth_admin = Annotated[Session, Depends(CheckAuth("admin"))]

@router.post("/list")
async def list_of_products(db: db, _: auth):
    return await products_list(db)
