from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import PositionModel, EmployeeModel
from schemas import PositionListItemResponseSchema, PositionCreateRequestSchema, PositionUpdateRequestSchema


async def fetch_position_by_id(position_id: int, db: AsyncSession) -> PositionModel:
    stmt = select(PositionModel).options(
        selectinload(PositionModel.employees).selectinload(EmployeeModel.department),
    ).where(PositionModel.id == position_id)
    result = await db.execute(stmt)
    position = result.scalar_one_or_none()

    return position


async def fetch_positions(offset: int, limit: int, db: AsyncSession) -> list[PositionListItemResponseSchema]:
    order_by: list = PositionModel.default_order_by()  # a list with ordering settings for model
    stmt = select(PositionModel)

    if order_by:
        # apply default_order_by only if it's overridden (from BaseModel it contains only [None])
        stmt = stmt.order_by(*order_by)

    stmt = stmt.offset(offset).limit(limit)

    result_positions = await db.execute(stmt)
    positions = result_positions.scalars().all()

    return [PositionListItemResponseSchema.model_validate(position) for position in positions]


async def create_position_entity(
        position_data: PositionCreateRequestSchema,
        db: AsyncSession
) -> PositionModel:
    existing_stmt = select(PositionModel).where(PositionModel.title == position_data.title)
    existing_result = await db.execute(existing_stmt)
    existing_position = existing_result.scalar_one_or_none()

    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A position with title {position_data.title} already exists."
        )

    try:
        new_position = PositionModel(**position_data.model_dump())

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


async def update_position_entity(position_id: int, update_data: PositionUpdateRequestSchema, db: AsyncSession) -> None:
    stmt = select(PositionModel).where(PositionModel.id == position_id)
    position = (await db.execute(stmt)).scalar_one_or_none()

    if position is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position with specified ID was not found."
        )

    if update_data.title:
        # check if exists position with the same title
        stmt = select(PositionModel).where(PositionModel.title == update_data.title)
        same_title_position: PositionModel | None = (await db.execute(stmt)).scalar_one_or_none()

        if same_title_position:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A position with title {update_data.title} already exists."
            )

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(position, field, value)

    try:
        await db.commit()
        await db.refresh(position, ["employees"])
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )
