from typing import Annotated

from fastapi import APIRouter, Query, Depends, Path, Body, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database.models import PositionModel
from schemas import (
    PositionListResponseSchema,
    PositionDetailResponseModel,
    PositionCreateSchema
)
from database import get_db


router = APIRouter()


@router.get(
    "/positions/",
    response_model=list[PositionListResponseSchema],
)
async def get_position_list(
        page: Annotated[int, Query(ge=1, description="Page number (1-based index)")] = 1,
        per_page: Annotated[int, Query(ge=1, le=20, description="Number of items per page")] = 10,
        db: AsyncSession = Depends(get_db)
):
    ...


@router.get(
    "/positions/{position_id}/",
    response_model=PositionDetailResponseModel
)
async def get_position_detail(
        position_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)
):
    ...


@router.post(
    "/positions/",
    response_model=PositionDetailResponseModel
)
async def create_position(
        data: Annotated[PositionCreateSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    existing_stmt = select(PositionModel).where(PositionModel.title == data.title)
    existing_result = await db.execute(existing_stmt)
    existing_position = existing_result.scalars().first()

    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A position with title {data.title} already exists."
        )

    try:
        position = PositionModel(
            title=data.title,
            rate=data.rate,
            employees=data.employees,
        )

        db.add(employee)
        await db.commit()
        await db.refresh(position, ["employees"])

        return Position

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input data."
        )
