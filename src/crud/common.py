from typing import Type

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import BaseModel


async def count_entities(model: Type[BaseModel], db: AsyncSession) -> int:
    """
    Calculate amount of an entities in a table with specified SQLAlchemy model.

    If there is no entities then this method raises HTTPException (404).

    :param model: SQLAlchemy model
    :param db: Async session with the database
    :return: amount of entities
    :raises HTTPException: if there was found 0 entities
    """
    count_stmt = select(func.count(model.id))
    result_count = await db.execute(count_stmt)
    total_entities = result_count.scalar_one_or_none()

    if not total_entities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No departments was found."
        )

    return total_entities
