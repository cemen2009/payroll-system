from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import DepartmentModel, EmployeeModel
from schemas import DepartmentListItemSchema, DepartmentCreateSchema


async def fetch_department_by_id(department_id: int, db: AsyncSession) -> DepartmentModel:
    """
    Retrieve a single Department ORM-model entity by its ID, including its related employees and chief.

    This function executes an asynchronous SQLAlchemy query to fetch a DepartmentModel instance
    with the specified ID. It eagerly loads the `employees` and `chief` relationships using `selectinload`
    to avoid lazy-loading issues and multiple queries.

    :param department_id: ID of fetched department
    :param db: Async session with the database
    :return: DepartmentModel instance with `employees` and `chief` loaded
    :raises HTTPException: if no department exists with the given ID (404)
    """
    stmt = select(DepartmentModel).options(
        selectinload(DepartmentModel.employees),
        selectinload(DepartmentModel.chief)
    ).where(DepartmentModel.id == department_id)

    result = await db.execute(stmt)
    department = result.scalar_one_or_none()

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department with specified ID was not found."
        )

    return department


async def fetch_departments(offset: int, limit: int, db: AsyncSession) -> list[DepartmentListItemSchema]:
    order_by: list = DepartmentModel.default_order_by()
    stmt = select(DepartmentModel)

    if order_by:
        stmt = stmt.order_by(*order_by)

    stmt = stmt.offset(offset).limit(limit)
    result_departments = await db.execute(stmt)
    departments = result_departments.scalars().all()

    if not departments:
        # TODO: put here custom exception
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No departments was found on page {limit}."
        )

    departments_list = [DepartmentListItemSchema.model_validate(department) for department in departments]

    return departments_list


async def create_department_entity(
        department_data: DepartmentCreateSchema,
        db: AsyncSession
) -> DepartmentModel:
    stmt = select(DepartmentModel).where(
        DepartmentModel.code == department_data.code
    )
    existing_department_result = await db.execute(stmt)
    existing_department = existing_department_result.scalar_one_or_none()

    if existing_department:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department with specified code already exists."
        )

    if department_data.chief_id is not None:
        stmt = select(EmployeeModel).where(
            EmployeeModel.id == department_data.chief_id
        )
        chief_result = await db.execute(stmt)
        chief = chief_result.scalar_one_or_none()

        if chief is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chief with specified ID was not found."
            )

    try:
        new_department = DepartmentModel(
            **department_data.model_dump()
        )

        db.add(new_department)
        await db.commit()
        await db.refresh(new_department, ["chief", "employees"])

        return new_department

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )


# async def update_department_entity(update_data: DepartmentUpdateSchema, db: AsyncSession) -> None:
#     ...


async def delete_department_entity(department_id: int, db: AsyncSession) -> None:
    stmt = select(DepartmentModel).where(DepartmentModel.id == department_id)
    result = await db.execute(stmt)
    department = result.scalar_one_or_none()

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department with specified ID was not found."
        )

    await db.delete(department)
    await db.commit()
