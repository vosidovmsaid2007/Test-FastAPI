from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import auth, user, application
from core.config import DBInstance
from db.base import BaseDBModel
from dto.application import HealthCheck
from utils.aioclient import HttpClientInstance


@asynccontextmanager
async def lifespan(fastapi: FastAPI) -> None:    
    await DBInstance.init_orm()
    await DBInstance.create_default_user()
    await DBInstance.create_default_product()
    HttpClientInstance.start()
    yield
    await DBInstance.teardown_orm()
    await HttpClientInstance.stop()
    await HttpClientInstance.stop()

app = FastAPI(title="Task", lifespan=lifespan)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(application.router)

@app.get("/health", response_model=HealthCheck, include_in_schema=False)
async def get_health() -> HealthCheck:
    """Perform a Health Check."""
    return HealthCheck(status="OK")

db_metadata = BaseDBModel.metadata
