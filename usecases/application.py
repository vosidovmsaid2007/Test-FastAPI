from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.application import Product
from dto.application import ProductsOutList

async def products_list(db: AsyncSession) -> ProductsOutList:
    products = await db.scalars(select(Product))
    return [ProductsOutList(
        created_at=product.created_at,
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price
    ) for product in products]
