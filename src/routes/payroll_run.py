from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud import (
    count_entities,
    fetch_payrolls,
    fetch_payroll_by_id,
    create_payroll_run_entity,
    approve_payroll_run_entity
)
from database import get_db
from exceptions import NotFoundEntityException
from exceptions.common import ConflictEntityException
from models import PayrollRunModel
from schemas import PayrollRunListResponseSchema, PayrollRunDetailResponseSchema


router = APIRouter()


@router.post(
    "/generate/",
    response_model=PayrollRunDetailResponseSchema,
    summary="Generate a payroll for a month, with cogenerated salary lines for all employees in all departments",
    status_code=status.HTTP_201_CREATED,
)
async def create_payroll_run(
        year: Annotated[int, Query()],
        month: Annotated[int, Query()],
        db: AsyncSession = Depends(get_db)
):
    try:
        payroll_run = await create_payroll_run_entity(year, month, db)
    except ConflictEntityException:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Payroll run already exists.")

    return payroll_run


@router.get(
    "/",
    response_model=PayrollRunListResponseSchema,
    summary="Fetch list of payroll runs with specified pagination."
)
async def get_payrolls(
        per_page: Annotated[int, Query(ge=1, le=20)] = 10,
        page: Annotated[int, Query(ge=1)] = 1,
        db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page

    total = await count_entities(PayrollRunModel, db)
    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payrolls were found."
        )

    payrolls = await fetch_payrolls(offset, per_page, db)
    response = PayrollRunListResponseSchema(total=total, items=payrolls)
    return response


@router.get(
    "/{payroll_id}/",
    response_model=PayrollRunDetailResponseSchema,
    summary="Fetch a payroll run with specified payroll ID.",
)
async def get_payroll(
        payroll_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db),
):
    try:
        payroll = await fetch_payroll_by_id(payroll_id, db)
    except NotFoundEntityException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.msg
        )

    return payroll


@router.post(
    "/{payroll_id}/approve",
    response_model=PayrollRunDetailResponseSchema,
    summary="Approve payroll run by ID",
    status_code=status.HTTP_200_OK,
)
async def approve_payroll_run(
    payroll_id: Annotated[int, Path()],
    db: AsyncSession = Depends(get_db),
):
    try:
        payroll = await approve_payroll_run_entity(payroll_id, db)
    except NotFoundEntityException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll run not found."
        )
    except ConflictEntityException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payroll run is already approved."
        )

    return payroll
