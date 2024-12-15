import os
from dotenv import load_dotenv

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from db.user import User
from db.application import Product
from dto.static_types import Role
from services.otp import EmailOTPService

EmailOTPService = EmailOTPService()

load_dotenv()
class Database:
    CONNECTION_STRING = os.getenv("CONNECTION_STRING")

    async def init_orm(self) -> None:
        self.ENGINE = create_async_engine(self.CONNECTION_STRING, echo=bool(os.getenv("DEBUG")))
        self.SESSION_MAKER = async_sessionmaker(self.ENGINE, expire_on_commit=False)

    async def teardown_orm(self) -> None:
        await self.ENGINE.dispose()

    async def create_default_user(self) -> None:
        async with self.SESSION_MAKER() as s:
            z = await s.scalar(select(User).where(User.email=="msaidvosidov@gmail.com"))
            if z is None:
                await s.scalar(insert(User).values({"email": "msaidvosidov@gmail.com",
                                                    "name": "Msaid",
                                                    "surname": "Vosidov",
                                                    "password": await User.hash_password("msaid2007"),
                                                    "role": Role.admin,
                                                    "is_confirmed": True,
                                                    "confirmation_token": await User.hash_password(await EmailOTPService.generate_otp())}))
            await s.commit()

    async def create_default_product(self) -> None:
        async with self.SESSION_MAKER() as s:
            z = await s.scalar(select(Product).where(Product.id==1))
            if z is None:
                await s.scalar(insert(Product).values({"name": "Product 1",
                                                        "description": "Description 1",
                                                        "price": 100}))
            await s.commit()
DBInstance = Database()
