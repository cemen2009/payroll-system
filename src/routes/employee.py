from fastapi import APIRouter, Request, Path, Depends, Body, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from models import EmployeeModel, PositionModel, DepartmentModel
from schemas import (
    EmployeeDetailResponseSchema,
    EmployeeListResponseSchema,
    EmployeeListItemSchema,
    EmployeeCreateSchema
)
from database import get_db


router = APIRouter()



@router.post(
    "/employee/",
    response_model=EmployeeDetailResponseSchema,
    summary="Create an employee with required position."
)
async def create_employee(
        employee_data: EmployeeCreateSchema,
        db: AsyncSession = Depends(get_db)
):
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
            ["position", "department", "work_reports", "salary_reports", "vacations"]
        )

        return employee

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )


@router.get(
    "/employees/"
)
async def list_employee(
        db: AsyncSession = Depends(get_db)
):
    ...
