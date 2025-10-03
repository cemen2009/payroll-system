from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select, extract, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import VacationModel, EmployeeModel
from schemas import (
    VacationListItemResponseSchema,
    VacationCreateRequestSchema,
    VacationUpdateRequestSchema
)
from config import get_settings


VACATION_LIMIT_PERCENTAGE = get_settings().VACATION_LIMIT_PERCENTAGE


async def calculate_vacations_percentage(department_id: int, db: AsyncSession) -> float:
    """Returns % of employee with active vacations."""
    today = date.today()

    stmt = select(func.count()).select_from(EmployeeModel).where(
        EmployeeModel.department_id == department_id
    )
    total_employee = (await db.execute(stmt)).scalar_one()

    if total_employee == 0:
        return 0

    active_vacation_stmt = (
        select(func.count(func.distinct(EmployeeModel.id)))
        .join(VacationModel, VacationModel.employee_id == EmployeeModel.id)
        .where(EmployeeModel.department_id == department_id)
        .where(VacationModel.start_date <= today)
        .where(VacationModel.end_date >= today)
    )
    active_vacation_employees = (await db.execute(active_vacation_stmt)).scalar_one()

    return (active_vacation_employees / total_employee) * 100


async def fetch_vacation_by_id(vacation_id: int, db: AsyncSession) -> VacationModel | None:
    stmt = select(VacationModel).options(
        selectinload(VacationModel.employee),
    ).where(VacationModel.id == vacation_id)
    result = await db.execute(stmt)
    position = result.scalar_one_or_none()

    return position


async def fetch_vacations(offset: int, limit: int, db: AsyncSession) -> list[VacationListItemResponseSchema | None]:
    order_by: list = VacationModel.default_order_by()  # a list with ordering settings for model
    stmt = select(VacationModel)

    if order_by:
        # apply default_order_by only if it's overridden (from BaseModel it contains only [None])
        stmt = stmt.order_by(*order_by)

    stmt = stmt.offset(offset).limit(limit)

    vacations = (await db.execute(stmt)).scalars().all()

    return [VacationListItemResponseSchema.model_validate(vacation) for vacation in vacations]


async def create_vacation_entity(
        vacation_data: VacationCreateRequestSchema,
        db: AsyncSession
) -> VacationModel:
    stmt = select(EmployeeModel).where(EmployeeModel.id == vacation_data.employee_id)
    employee: EmployeeModel | None = (await db.execute(stmt)).scalar_one_or_none()

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {vacation_data.employee_id} doesn't exist."
        )

    active_vacations_percentage = await calculate_vacations_percentage(employee.department_id, db)
    print(f"DEBUG: active vacation percentage {active_vacations_percentage}%")
    print(f"DEBUG: checking vacation availability {active_vacations_percentage}% >= {VACATION_LIMIT_PERCENTAGE}%")
    if active_vacations_percentage >= VACATION_LIMIT_PERCENTAGE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You can not create vacation when {VACATION_LIMIT_PERCENTAGE}% "
                   f"employees of a department is already in vacations."
        )

    existing_stmt = select(VacationModel).where(
        and_(
            extract("year", VacationModel.start_date) == vacation_data.start_date.year,
            VacationModel.employee_id == vacation_data.employee_id,
        )
    )
    existing_vacation = (await db.execute(existing_stmt)).scalar_one_or_none()

    if existing_vacation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vacation for employee #{vacation_data.employee_id} already registered for that year.",
        )

    try:
        new_vacation = VacationModel(**vacation_data.model_dump())

        db.add(new_vacation)
        await db.commit()
        await db.refresh(new_vacation, ["employee"])

        return new_vacation
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )


async def update_vacation_entity(vacation_id: int, update_data: VacationUpdateRequestSchema, db: AsyncSession) -> None:
    stmt = select(VacationModel).where(VacationModel.id == vacation_id)
    vacation = (await db.execute(stmt)).scalar_one_or_none()

    if vacation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacation with specified ID was not found."
        )

    if update_data.start_date:
        # check if exists vacation for specified year for an employee
        stmt = select(VacationModel).where(
            and_(
                extract("year", VacationModel.start_date) == update_data.start_date.year,
                VacationModel.employee_id == update_data.employee_id,
            )
        )
        same_year_vacation: VacationModel | None = (await db.execute(stmt)).scalar_one_or_none()

        if same_year_vacation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Vacation for employee #{update_data.employee_id} already registered for that year."
            )

    if update_data.employee_id:
        stmt = select(EmployeeModel).where(EmployeeModel.id == update_data.employee_id)
        employee = (await db.execute(stmt)).scalar_one_or_none()

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee with specified ID was not found."
            )

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(vacation, field, value)

    try:
        await db.commit()
        await db.refresh(vacation, ["employee"])
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )
