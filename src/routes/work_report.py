from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from crud import count_entities, delete_entity
from crud import (
    fetch_work_report,
    fetch_work_reports,
    create_work_report_entity,
    update_work_report_entity,
)
from database import get_db
from exceptions import NotFoundEntityException
from exceptions.common import ConflictEntityException, BadRequestException
from models import WorkReportModel
from schemas import (
    WorkReportListResponseSchema,
    WorkReportDetailResponseSchema,
    WorkReportCreateRequestSchema,
    WorkReportUpdateRequestSchema,
)


router = APIRouter()


@router.get(
    "/work_reports/",
    response_model=WorkReportListResponseSchema,
    summary="Get list of work reports with a pagination."
)
async def get_work_reports_list(
        page: Annotated[int, Query(ge=1)] = 1,
        per_page: Annotated[int, Query(ge=1, le=20)] = 10,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page
    total = await count_entities(WorkReportModel, db)

    if not total:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No work reports were found."
        )

    reports = await fetch_work_reports(offset, per_page, db)

    response = WorkReportListResponseSchema(
        total=total,
        items=reports
    )
    return response


@router.get(
    "/work_reports/{report_id}/",
    response_model=WorkReportDetailResponseSchema,
    summary="Get a specific work report by ID."
)
async def get_work_report(
        report_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)
):
    try:
        work_report = await fetch_work_report(report_id, db)
    except NotFoundEntityException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work report with the given ID was not found."
        )

    return work_report


@router.post(
    "/work_reports/",
    response_model=WorkReportDetailResponseSchema,
    summary="Create a work report with provided schema in body."
)
async def create_work_report(
        data: Annotated[WorkReportCreateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    try:
        work_report = await create_work_report_entity(data, db)
    except ConflictEntityException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Work report for this employee already exists."
        )
    except NotFoundEntityException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee with give ID was not found."
        )
    except BadRequestException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )

    return work_report


@router.patch(
    "/work_reports/{report_id}/",
    status_code=status.HTTP_200_OK,
    summary="Update a work report with provided patch schema in body."
)
async def update_work_report(
        report_id: Annotated[int, Path()],
        data: Annotated[WorkReportUpdateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    try:
        await update_work_report_entity(report_id, data, db)
    except BadRequestException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong input data."
        )
    except NotFoundEntityException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.msg
        )
    except ConflictEntityException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.msg
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": f"Work Report #{report_id} was updated successfully."}
    )


@router.delete(
    "/work_reports/{report_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a work report with provided ID in path."
)
async def remove_work_report(
        report_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)
):
    try:
        await delete_entity(WorkReportModel, report_id, db)
    except NotFoundEntityException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work report with the given ID was not found."
        )
