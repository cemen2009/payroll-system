from typing import Annotated

from fastapi import APIRouter, Path, Depends, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from models import DepartmentModel, EmployeeModel
from schemas import (
    DepartmentDetailResponseSchema,
    DepartmentCreateSchema,
    DepartmentListResponseSchema,
    DepartmentListItemSchema
)
from database import get_db


router = APIRouter()


@router.get(
    "/departments/{department_id}/",
    response_model=DepartmentDetailResponseSchema,
    summary="Get a department with specified ID."
)
async def read_department_detail(
        department_id: Annotated[int, Path(ge=1)],
        db: AsyncSession = Depends(get_db)
):
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


@router.get(
    "/departments/",
    response_model=DepartmentListResponseSchema,
    summary="Get all departments with specified pagination."
)
async def read_department_list(
        request: Request,
        per_page: Annotated[int, Path(ge=1, le=20)] = 10,
        page: Annotated[int, Path(ge=1)] = 1,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    count_stmt = select(func.count(DepartmentModel.id))
    result_count = await db.execute(count_stmt)
    total_departments = result_count.scalar_one_or_none()

    if not total_departments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No departments was found."
        )

    order_by: list = DepartmentModel.default_order_by()
    stmt = select(DepartmentModel)

    if order_by:
        stmt = stmt.order_by(*order_by)

    stmt = stmt.offset(offset).limit(per_page)
    result_departments = await db.execute(stmt)
    departments = result_departments.scalars().all()

    if not departments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No departments was found on page {page}."
        )

    departments_list = [DepartmentListItemSchema.model_validate(department) for department in departments]

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


@router.post(
    "/departments/",
    response_model=DepartmentDetailResponseSchema,
    summary="Create a new department."
)
async def create_department(
        department_data: Annotated[DepartmentCreateSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
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


@router.delete(
    "/department/{department_id}/",
    summary="Delete a department with specific ID."
)
async def remove_department(
    department_id: Annotated[int, Path(ge=1)],
    db: AsyncSession = Depends(get_db)
):
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

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Department #{department_id} was deleted successfully."}
    )


# TODO: implement PUT endpoint
