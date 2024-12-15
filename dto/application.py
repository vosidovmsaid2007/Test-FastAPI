from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from dto.user import UserOut

class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"

class ProductsOutList(BaseModel):
    created_at: datetime
    id: int
    name: str | None
    description: str | None
    price: float | None

    class Config:
        from_attributes = True