from typing import Annotated

from fastapi import APIRouter, Query, Path, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from crud import count_entities, fetch_vacations, fetch_vacation_by_id, create_vacation_entity, delete_entity, \
    update_vacation_entity
from database import get_db
from exceptions import NotFoundEntityException
from models import VacationModel
from schemas import VacationListResponseSchema, VacationCreateRequestSchema, VacationDetailResponseSchema, \
    VacationUpdateRequestSchema

router = APIRouter()


@router.get(
    "/vacations/",
    response_model=VacationListResponseSchema,
    summary="Get a list of vacations.",
    responses={
        404: {"detail": "No vacations were found."},
    }
)
async def get_vacations(
        page: Annotated[int, Query(ge=1, description="Page number (1-based index)")] = 1,
        per_page: Annotated[int, Query(ge=1, le=20, description="Number of items per page")] = 10,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    total_items = await count_entities(VacationModel, db)

    if not total_items:
        raise HTTPException(status_code=404, detail="No vacations were found.")

    vacations_list = await fetch_vacations(offset, per_page, db)
    response = VacationListResponseSchema(vacations=vacations_list, total=total_items)

    return response


@router.get(
    "/vacations/{vacation_id}/",
    response_model=VacationDetailResponseSchema,
    summary="Fetch detail about certain vacation with specific ID.",
    responses={404: {"detail": "No vacation was found."}}
)
async def get_vacation_detail(
        vacation_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)
):
    vacation = await fetch_vacation_by_id(vacation_id, db)

    if vacation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No vacation was found.")

    return vacation


@router.post(
    "/vacations/",
    response_model=VacationDetailResponseSchema,
    summary="Create a new vacation for an employee",
    responses={
        409: {"detail": "Vacation for that year already registered."},
        404: {"detail": "Employee with specified ID was not found."}
    }
)
async def create_vacation(
        vacation_date: Annotated[VacationCreateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    new_vacation = await create_vacation_entity(vacation_date, db)
    return new_vacation


@router.patch(
    "/vacations/{vacation_id}/",
    status_code=status.HTTP_200_OK,
    responses={
        409: {"detail": "Vacation for that year already registered."},
        404: {"detail": "Employee with specified ID was not found."}
    }
)
async def update_vacation(
        vacation_id: Annotated[int, Path()],
        update_data: Annotated[VacationUpdateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    await update_vacation_entity(vacation_id, update_data, db)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Vacation #{vacation_id} was updated successfully."}
    )


@router.delete(
    "/vacations/{vacation_id}",
    summary="Delete a vacation.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"detail": "No vacation was found."}}
)
async def delete_vacation(
        vacation_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)
):
    try:
        await delete_entity(VacationModel, vacation_id, db)
    except NotFoundEntityException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vacation was found."
        )
