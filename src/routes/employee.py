from typing import Annotated

from fastapi import APIRouter, Request, Path, Depends, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud import create_employee_entity, fetch_employee_by_id, count_entities, fetch_employees, delete_employee_entity
from models import EmployeeModel, PositionModel, DepartmentModel
from schemas import (
    EmployeeDetailResponseSchema,
    EmployeeListResponseSchema,
    EmployeeListItemSchema,
    EmployeeCreateSchema
)
from database import get_db


router = APIRouter()


@router.get(
    "/employees/",
    response_model=EmployeeListResponseSchema,
    summary="Fetch employees with specified pagination settings."
)
async def get_employees_list(
        request: Request,
        page: Annotated[int, Path(ge=1)] = 1,
        per_page: Annotated[int, Path(ge=1, le=20)] = 10,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    total_items = await count_entities(EmployeeModel, db)
    employees = await fetch_employees(offset, per_page, db)

    total_pages = (total_items + per_page - 1) // per_page

    url_path = request.url
    query_base = f"{url_path}?per_page={per_page}"

    prev_page = f"{query_base}&page={page - 1}" if page > 1 else None
    next_page = f"{query_base}&page={page + 1}" if page < total_pages else None

    response = EmployeeListResponseSchema(
        employees=employees,
        total_pages=total_pages,
        total_employees=total_items,
        next_page=next_page,
        previous_page=prev_page,
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
        employee_data: Annotated[EmployeeCreateSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    new_employee = await create_employee_entity(employee_data, db)
    return new_employee


# @router.put(
#     "/employee/{employee_id}/",
#     summary="Update an employee with required position."
# )
# async def update_employee(
#         employee_id: Annotated[int, Path(ge=1)],
#         db: AsyncSession = Depends(get_db),
# ):
#     ...


@router.delete(
    "/employee/{employee_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an employee with specified ID."
)
async def delete_employee(
        employee_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db),
):
    await delete_employee_entity(employee_id, db)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Employee #{employee_id} was deleted successfully."}
    )
