from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from schemas import EmployeeListItemResponseSchema, EmployeeCreateRequestSchema, EmployeeUpdateRequestSchema
from models import EmployeeModel, PositionModel, DepartmentModel


async def fetch_employee_by_id(employee_id: int, db: AsyncSession) -> EmployeeModel:
    stmt = select(EmployeeModel).options(
        selectinload(EmployeeModel.department),
        selectinload(EmployeeModel.position),
        selectinload(EmployeeModel.work_reports),
        selectinload(EmployeeModel.work_reports),
        selectinload(EmployeeModel.vacations),
    ).where(EmployeeModel.id == employee_id)

    employee_result = await db.execute(stmt)
    employee = employee_result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee with specified ID was not found."
        )

    return employee


async def fetch_employees(offset: int, limit: int, db: AsyncSession) -> list[EmployeeListItemResponseSchema]:
    order_by: list = EmployeeModel.default_order_by()
    stmt = select(EmployeeModel).options(
        selectinload(EmployeeModel.department),
        selectinload(EmployeeModel.position)
    )

    if order_by:
        stmt = stmt.order_by(*order_by)

    stmt = stmt.offset(offset).limit(limit)
    employees_result = await db.execute(stmt)
    employees = employees_result.scalars().all()

    employees_list = [EmployeeListItemResponseSchema.model_validate(employee) for employee in employees]

    return employees_list


async def create_employee_entity(employee_data: EmployeeCreateRequestSchema, db: AsyncSession) -> EmployeeModel:
    stmt = select(EmployeeModel).where(
        or_(
            EmployeeModel.tab_number == employee_data.tab_number,
            EmployeeModel.social_security_number == employee_data.social_security_number,
        )
    )
    existing_employee_result = await db.execute(stmt)
    existing_employee = existing_employee_result.scalar_one_or_none()

    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Employee with that tab_number or social_number already exists."
        )

    existing_position = (await db.execute(
        select(PositionModel).where(PositionModel.id == employee_data.position_id)
    )).scalar_one_or_none()

    if existing_position is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position with specified ID was not found."
        )

    # department_id is nullable, so we check if it was specified first
    if employee_data.department_id:

        existing_department = (await db.execute(
            select(DepartmentModel).where(
                DepartmentModel.id == employee_data.department_id
            )
        )).scalar_one_or_none()

        if existing_department is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department with specified ID was not found."
            )

    try:
        employee = EmployeeModel(**employee_data.model_dump())

        db.add(employee)
        await db.commit()
        await db.refresh(
            employee,
            ["position", "department", "work_reports", "vacations"]
        )

        return employee

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )


async def update_employee_entity(employee_id: int, update_data: EmployeeUpdateRequestSchema, db: AsyncSession) -> None:
    stmt = select(EmployeeModel).where(EmployeeModel.id == employee_id)
    employee_result = await db.execute(stmt)
    employee = employee_result.scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee with specified ID was not found."
        )

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)

    try:
        await db.commit()
        await db.refresh(
            employee,
            ["position", "department", "vacations", "work_reports"]
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )
