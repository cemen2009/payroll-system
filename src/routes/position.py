from typing import Annotated

from fastapi import APIRouter, Query, Depends, Path, Body, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from database.models import PositionModel
from schemas import (
    PositionListResponseSchema,
    PositionDetailResponseSchema,
    PositionCreateSchema,
    PositionListItemSchema
)
from database import get_db


router = APIRouter()


@router.get(
    "/positions/",
    response_model=PositionListResponseSchema,
    summary="Get all positions from the database."
)
async def read_position_list(
        request: Request,
        page: Annotated[int, Query(ge=1, description="Page number (1-based index)")] = 1,
        per_page: Annotated[int, Query(ge=1, le=20, description="Number of items per page")] = 10,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    count_stmt = select(func.count(PositionModel.id))
    result_count = await db.execute(count_stmt)
    total_items = result_count.scalar() or 0

    if not total_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No positions was found."
        )

    order_by: list = PositionModel.default_order_by() # a list with ordering settings for model
    stmt = select(PositionModel)

    if order_by:
        # apply default_order_by only if it's overridden (from BaseModel it contains only [None])
        stmt = stmt.order_by(*order_by)

    stmt = stmt.offset(offset).limit(per_page)

    result_positions = await db.execute(stmt)
    positions = result_positions.scalars().all()

    if not positions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No positions was found on page {page}."
        )

    positions_list = [PositionListItemSchema.model_validate(position) for position in positions]

    total_pages = (total_items + per_page - 1) // per_page

    url_path = request.url
    query_base = f"{url_path}?per_page={per_page}"

    prev_page = f"{query_base}&page={page - 1}" if page > 1 else None
    next_page = f"{query_base}&page={page + 1}" if page < total_pages else None

    response = PositionListResponseSchema(
        positions=positions_list,
        previous_page=prev_page,
        next_page=next_page,
        total_positions=total_items,
        total_pages=total_pages
    )

    return response


@router.get(
    "/positions/{position_id}/",
    response_model=PositionDetailResponseSchema,
    summary="Get a position with specified ID."
)
async def read_position_detail(
        position_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db)
):
    stmt = select(PositionModel).options(
        selectinload(PositionModel.employees),
    ).where(PositionModel.id == position_id)
    result = await db.execute(stmt)
    position = result.scalar_one_or_none()

    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position with specified ID was not found."
        )

    return position


@router.post(
    "/positions/",
    response_model=PositionDetailResponseSchema,
    summary="Create new position with rate ($/hour)."
)
async def create_position(
        data: Annotated[PositionCreateSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    existing_stmt = select(PositionModel).where(PositionModel.title == data.title)
    existing_result = await db.execute(existing_stmt)
    existing_position = existing_result.scalar_one_or_none()

    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A position with title {data.title} already exists."
        )

    try:
        new_position = PositionModel(**data.model_dump())

        db.add(new_position)
        await db.commit()
        await db.refresh(new_position, ["employees"])

        return new_position
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )


@router.delete(
    "/positions/{position_id}/",
    summary="Delete a position with specific ID."
)
async def remove_position(
        position_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db)
):
    stmt = select(PositionModel).where(PositionModel.id == position_id)
    result = await db.execute(stmt)
    position = result.scalar_one_or_none()

    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position with specified ID was not found."
        )

    await db.delete(position)
    await db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Position #{position_id} was deleted successfully."}
    )


# TODO: implement PUT endpoint
