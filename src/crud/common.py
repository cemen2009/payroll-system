from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import NotFoundEntityException
from models.base import BaseModel


async def count_entities(model: type[BaseModel], db: AsyncSession) -> int | None:
    """
    Calculate amount of an entities in a table with specified SQLAlchemy model.

    If there is no entities then this method raises HTTPException (404).

    :param model: SQLAlchemy model
    :param db: Async session with the database
    :return: amount of entities
    :raises HTTPException: if there was found 0 entities
    """
    count_stmt = select(func.count(model.id)) # type: ignore
    result_count = await db.execute(count_stmt)
    total_entities = result_count.scalar_one_or_none()

    return total_entities


async def delete_entity(model: type[BaseModel], entity_id: int, db: AsyncSession) -> None:
    stmt = select(model).where(model.id == entity_id) # type: ignore
    result = await db.execute(stmt)
    position = result.scalar_one_or_none()

    if position is None:
        raise NotFoundEntityException

    await db.delete(position)
    await db.commit()
