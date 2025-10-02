from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import DepartmentModel, EmployeeModel
from schemas import (
    DepartmentListItemResponseSchema,
    DepartmentCreateRequestSchema,
    DepartmentUpdateRequestSchema
)


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
        selectinload(DepartmentModel.employees).selectinload(EmployeeModel.department),
        selectinload(DepartmentModel.chief).selectinload(EmployeeModel.department)
    ).where(DepartmentModel.id == department_id)

    result = await db.execute(stmt)
    department = result.scalar_one_or_none()

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department with specified ID was not found."
        )

    return department


async def fetch_departments(offset: int, limit: int, db: AsyncSession) -> list[DepartmentListItemResponseSchema]:
    order_by: list = DepartmentModel.default_order_by()
    stmt = select(DepartmentModel)

    if order_by:
        stmt = stmt.order_by(*order_by)

    stmt = stmt.offset(offset).limit(limit)
    result_departments = await db.execute(stmt)
    departments = result_departments.scalars().all()

    departments_list = [DepartmentListItemResponseSchema.model_validate(department) for department in departments]

    return departments_list


async def create_department_entity(
        department_data: DepartmentCreateRequestSchema,
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
        chief: EmployeeModel = chief_result.scalar_one_or_none()

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


async def update_department_entity(department_id: int, update_data: DepartmentUpdateRequestSchema, db: AsyncSession) -> None:
    stmt = select(DepartmentModel).where(DepartmentModel.id == department_id)
    department = (await db.execute(stmt)).scalar_one_or_none()

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department with specified ID was not found."
        )

    if update_data.chief_id is not None:
        chief_stmt = select(EmployeeModel).where(
            EmployeeModel.id == update_data.chief_id
        )
        chief: EmployeeModel = (await db.execute(chief_stmt)).scalar_one_or_none()

        if chief is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chief with specified ID was not found."
            )

        if chief.department and chief.department_id != department_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chief should belong to same department."
            )

    if update_data.code is not None:
        code_stmt = select(DepartmentModel).where(DepartmentModel.code == update_data.code)
        code = (await db.execute(code_stmt)).scalar_one_or_none()

        if code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department with specified code already exists."
            )

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(department, field, value)

    try:
        await db.commit()
        await db.refresh(department, ["chief", "employees"])
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )
