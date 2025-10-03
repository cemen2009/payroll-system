from typing import Annotated

from fastapi import APIRouter, Path, Depends, Body, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from crud import (
    count_entities,
    fetch_department_by_id,
    fetch_departments,
    create_department_entity,
    update_department_entity,
    delete_entity
)
from exceptions import NotFoundEntityException
from models import DepartmentModel
from schemas import (
    DepartmentDetailResponseSchema,
    DepartmentCreateRequestSchema,
    DepartmentListResponseSchema, DepartmentUpdateRequestSchema,
)
from database import get_db


router = APIRouter()


@router.get(
    "/departments/",
    response_model=DepartmentListResponseSchema,
    summary="Get all departments with specified pagination."
)
async def get_department_list(
        per_page: Annotated[int, Query(ge=1, le=20)] = 10,
        page: Annotated[int, Query(ge=1)] = 1,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    total_departments = await count_entities(DepartmentModel, db)

    if not total_departments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No departments were found."
        )

    departments_list = await fetch_departments(offset, per_page, db)

    response = DepartmentListResponseSchema(
        departments=departments_list,
        total=total_departments
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
        department_data: Annotated[DepartmentCreateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    new_department = await create_department_entity(department_data, db)
    return new_department


@router.patch(
    "/departments/{department_id}/",
    status_code=status.HTTP_200_OK,
    summary="Update a department with specific ID."
)
async def update_department(
        department_id: Annotated[int, Path(ge=1)],
        update_data: Annotated[DepartmentUpdateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db),
):
    await update_department_entity(department_id, update_data, db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Department #{department_id} was updated successfully."}
    )


@router.delete(
    "/departments/{department_id}/",
    summary="Delete a department with specific ID."
)
async def remove_department(
    department_id: Annotated[int, Path(ge=1)],
    db: AsyncSession = Depends(get_db)
):
    try:
        await delete_entity(DepartmentModel, department_id, db)
    except NotFoundEntityException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No department was found."
        )
