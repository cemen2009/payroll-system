from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes import (
    payroll_router
)
from database import engine
from database.models import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):

    # startup code:

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield

    # shutdown code:

app = FastAPI(
    lifespan=lifespan,
    title="Payroll System",
)

api_version_prefix = "/api/v1"

app.include_router(payroll_router, prefix=f"{api_version_prefix}/payroll", tags=["payroll"])
