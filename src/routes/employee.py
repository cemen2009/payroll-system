from typing import Annotated

from fastapi import APIRouter, Path, Depends, Body, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from crud import (
    create_employee_entity,
    fetch_employee_by_id,
    count_entities,
    fetch_employees,
    update_employee_entity,
    delete_entity
)
from exceptions import NotFoundEntityException
from models import EmployeeModel
from schemas import (
    EmployeeDetailResponseSchema,
    EmployeeListResponseSchema,
    EmployeeCreateRequestSchema,
    EmployeeUpdateRequestSchema
)
from database import get_db


router = APIRouter()


@router.get(
    "/employees/",
    response_model=EmployeeListResponseSchema,
    summary="Fetch employees with specified pagination settings."
)
async def get_employees_list(
        page: Annotated[int, Path(ge=1)] = 1,
        per_page: Annotated[int, Path(ge=1, le=20)] = 10,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    total_items = await count_entities(EmployeeModel, db)

    if not total_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employees were found."
        )

    employees = await fetch_employees(offset, per_page, db)

    response = EmployeeListResponseSchema(
        employees=employees,
        total=total_items
    )

    return response


@router.get(
    "/employees/{employee_id}/",
    response_model=EmployeeDetailResponseSchema,
    summary="Fetch detailed info about an employee with specific ID."
)
async def get_employee_detail(
        employee_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db)
):
    employee = await fetch_employee_by_id(employee_id, db)
    return employee


@router.post(
    "/employee/",
    response_model=EmployeeDetailResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create an employee with required position."
)
async def create_employee(
        employee_data: Annotated[EmployeeCreateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    new_employee = await create_employee_entity(employee_data, db)
    return new_employee


@router.patch(
    "/employee/{employee_id}/",
    summary="Update an employee with required position."
)
async def update_employee(
        employee_id: Annotated[int, Path(ge=1)],
        employee_data: Annotated[EmployeeUpdateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db),
):
    await update_employee_entity(employee_id, employee_data, db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Employee #{employee_id} was updated successfully."}
    )


@router.delete(
    "/employee/{employee_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an employee with specified ID."
)
async def delete_employee(
        employee_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db),
):
    try:
        await delete_entity(EmployeeModel, employee_id, db)
    except NotFoundEntityException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employee was found."
        )
