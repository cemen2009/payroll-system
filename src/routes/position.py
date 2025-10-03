from typing import Annotated

from fastapi import APIRouter, Query, Depends, Path, Body, HTTPException, status
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from crud import (
    count_entities,
    fetch_positions,
    fetch_position_by_id,
    create_position_entity,
    update_position_entity,
    delete_entity
)
from exceptions import NotFoundEntityException
from models import PositionModel
from schemas import (
    PositionListResponseSchema,
    PositionDetailResponseSchema,
    PositionCreateRequestSchema, PositionUpdateRequestSchema,
)
from database import get_db


router = APIRouter()


@router.get(
    "/positions/",
    response_model=PositionListResponseSchema,
    summary="Get all positions from the database."
)
async def get_position_list(
        page: Annotated[int, Query(ge=1, description="Page number (1-based index)")] = 1,
        per_page: Annotated[int, Query(ge=1, le=20, description="Number of items per page")] = 10,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    total_items = await count_entities(PositionModel, db)

    if not total_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No positions were found."
        )

    positions_list = await fetch_positions(offset, per_page, db)

    response = PositionListResponseSchema(
        positions=positions_list,
        total=total_items
    )

    return response


@router.get(
    "/positions/{position_id}/",
    response_model=PositionDetailResponseSchema,
    summary="Get a position with specified ID."
)
async def get_position_detail(
        position_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db)
):
    position = await fetch_position_by_id(position_id, db)

    if position is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No position was found.")

    return position


@router.post(
    "/positions/",
    response_model=PositionDetailResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new position with rate ($/hour)."
)
async def create_position(
        data: Annotated[PositionCreateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    new_position = await create_position_entity(data, db)
    return new_position


@router.patch(
    "/positions/{position_id}/",
    status_code=status.HTTP_200_OK,
    summary="Update a position with specified ID."
)
async def update_position(
        position_id: Annotated[int, Path(ge=1)],
        update_data: Annotated[PositionUpdateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db),
):
    await update_position_entity(position_id, update_data, db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Position #{position_id} updated successfully."}
    )


@router.delete(
    "/positions/{position_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a position with specific ID."
)
async def remove_position(
        position_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db)
):
    try:
        await delete_entity(PositionModel, position_id, db)
    except NotFoundEntityException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No position was found."
        )
