from __future__ import annotations

from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from fastapi.exceptions import HTTPException
import jwt
import bcrypt
from sqlalchemy import ForeignKey, and_, insert, select, update
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import mapped_column, relationship, selectinload
from sqlalchemy.types import UUID, BigInteger, Boolean, DateTime, Enum, String, Text, Double

from db.base import BaseDBModel

class Product(AsyncAttrs, BaseDBModel):
    __tablename__ = "products"

    id = mapped_column(BigInteger, primary_key=True)
    name = mapped_column(String(255), nullable=True)
    description = mapped_column(Text, nullable=True)
    price = mapped_column(Double, default=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp())
