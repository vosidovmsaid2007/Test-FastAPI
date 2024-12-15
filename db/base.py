from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.types import DateTime


class BaseDBModel(DeclarativeBase):
    created_at = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    async def to_dict(self) -> dict:
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

    async def update_from_dict(self, **kwargs: dict) -> None:
        for arg in kwargs:
            if hasattr(self, arg):
                setattr(self, arg, kwargs[arg])

    async def include(self, fields: list) -> dict:
        fieldset = await self.to_dict()
        [fieldset.pop(field) for field in fieldset if field not in fields]
        return fieldset

    async def exclude(self, fields: list) -> dict:
        fieldset = await self.to_dict()
        [fieldset.pop(field) for field in fields]
        return fieldset
