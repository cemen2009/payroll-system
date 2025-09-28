from typing import Annotated

from fastapi import APIRouter, Path, Depends, Request, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud import (
    count_entities,
    fetch_department_by_id,
    fetch_departments,
    create_department_entity,
    delete_department_entity,
)
from models import DepartmentModel
from schemas import (
    DepartmentDetailResponseSchema,
    DepartmentCreateSchema,
    DepartmentListResponseSchema,
)
from database import get_db


router = APIRouter()


@router.get(
    "/departments/",
    response_model=DepartmentListResponseSchema,
    summary="Get all departments with specified pagination."
)
async def get_department_list(
        request: Request,
        per_page: Annotated[int, Path(ge=1, le=20)] = 10,
        page: Annotated[int, Path(ge=1)] = 1,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    total_departments = await count_entities(DepartmentModel, db)
    departments_list = await fetch_departments(offset, per_page, db)

    total_pages = (total_departments + per_page - 1) // per_page

    url_path = request.url
    query_base = f"{url_path}?per_page={per_page}"

    prev_page = f"{query_base}&page={page - 1}" if page > 1 else None
    next_page = f"{query_base}&page={page + 1}" if page < total_pages else None

    response = DepartmentListResponseSchema(
        departments=departments_list,
        total_departments=total_departments,
        total_pages=total_pages,
        next_page=next_page,
        previous_page=prev_page
    )

    return response


@router.get(
    "/departments/{department_id}/",
    response_model=DepartmentDetailResponseSchema,
    summary="Get a department with specified ID."
)
async def get_department_detail(
        department_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db)
):
    department = await fetch_department_by_id(department_id, db)
    return department


@router.post(
    "/departments/",
    response_model=DepartmentDetailResponseSchema,
    summary="Create a new department."
)
async def create_department(
        department_data: Annotated[DepartmentCreateSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    new_department = await create_department_entity(department_data, db)
    return new_department


@router.delete(
    "/department/{department_id}/",
    summary="Delete a department with specific ID."
)
async def remove_department(
    department_id: Annotated[int, Path(ge=1)],
    db: AsyncSession = Depends(get_db)
):
    await delete_department_entity(department_id, db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Department #{department_id} was deleted successfully."}
    )


# TODO: implement PUT endpoint
