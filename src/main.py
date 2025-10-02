from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes import (
    position_router,
    department_router,
    employee_router,
    vacation_router
)
from database import engine
from models import BaseModel


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

app.include_router(position_router, prefix=f"{api_version_prefix}/positions", tags=["Positions"])
app.include_router(department_router, prefix=f"{api_version_prefix}/departments", tags=["Departments"])
app.include_router(employee_router, prefix=f"{api_version_prefix}/employees", tags=["Employees"])
app.include_router(vacation_router, prefix=f"{api_version_prefix}/vacations", tags=["Vacations"])
