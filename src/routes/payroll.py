from typing import Annotated

from fastapi import APIRouter, Query, Depends, Path, Body

from sqlalchemy.ext.asyncio import AsyncSession

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
    ...
