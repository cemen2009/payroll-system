from typing import Annotated

from fastapi import APIRouter, Query, Depends, Path, Body, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from crud import (
    count_entities,
    fetch_positions,
    fetch_position_by_id,
    delete_position_entity,
    create_position_entity
)
from models import PositionModel
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
async def get_position_list(
        request: Request,
        page: Annotated[int, Query(ge=1, description="Page number (1-based index)")] = 1,
        per_page: Annotated[int, Query(ge=1, le=20, description="Number of items per page")] = 10,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    total_items = await count_entities(PositionModel, db)
    positions_list = await fetch_positions(offset, per_page, db)

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
async def get_position_detail(
        position_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db)
):
    position = await fetch_position_by_id(position_id, db)
    return position


@router.post(
    "/positions/",
    response_model=PositionDetailResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new position with rate ($/hour)."
)
async def create_position(
        data: Annotated[PositionCreateSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    new_position = await create_position(data, db)
    return new_position


# @router.put(
#     "/positions/{position_id}/",
#     summary="Update a position with specified ID."
# )
# async def update_position(
#         position_id: Annotated[int, Path(ge=1)],
#         db: AsyncSession = Depends(get_db),
# ):
#     ...


@router.delete(
    "/positions/{position_id}/",
    status_code=status.HTTP_200_OK,
    summary="Delete a position with specific ID."
)
async def remove_position(
        position_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db)
):
    await delete_position_entity(position_id, db)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Position #{position_id} was deleted successfully."}
    )
