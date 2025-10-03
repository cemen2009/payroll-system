from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from exceptions.common import ConflictEntityException, BadRequestException
from models import WorkReportModel, EmployeeModel
from exceptions import NotFoundEntityException
from schemas import (
    WorkReportCreateRequestSchema,
    WorkReportUpdateRequestSchema,
    WorkReportListItemResponseSchema,
)


async def fetch_work_reports(offset: int, limit: int, db: AsyncSession) -> list[WorkReportListItemResponseSchema]:
    order_by: list = WorkReportModel.default_order_by()
    stmt = select(WorkReportModel)

    if order_by:
        stmt = stmt.order_by(*order_by)

    stmt = stmt.offset(offset).limit(limit)
    reports = (await db.execute(stmt)).scalars().all()

    reports_list = [WorkReportListItemResponseSchema.model_validate(report) for report in reports]

    return reports_list


async def fetch_work_report(report_id: int, db: AsyncSession) -> WorkReportModel:
    """
    Retrieve a work report by id.

    :param report_id: ID of the work report
    :param db: Async session with the database
    :return: WorkReportModel instance from the database
    :raises NotFoundEntityException: If there is no work report with the given id
    """
    stmt = select(WorkReportModel).options(
        selectinload(WorkReportModel.employee)
    ).where(WorkReportModel.id == report_id)
    report = (await db.execute(stmt)).scalar_one_or_none()

    if report is None:
        raise NotFoundEntityException

    return report


async def create_work_report_entity(data: WorkReportCreateRequestSchema, db: AsyncSession) -> WorkReportModel:
    existing_report_stmt = select(WorkReportModel).where(
        and_(
            WorkReportModel.employee_id == data.employee_id,
            WorkReportModel.work_date == data.work_date,
        )
    )
    existing_report = (await db.execute(existing_report_stmt)).scalar_one_or_none()
    if existing_report:
        raise ConflictEntityException

    existing_employee_stmt = select(EmployeeModel).where(EmployeeModel.id == data.employee_id)
    employee = (await db.execute(existing_employee_stmt)).scalar_one_or_none()
    if employee is None:
        raise NotFoundEntityException

    try:
        report = WorkReportModel(**data.model_dump())

        db.add(report)
        await db.commit()
        await db.refresh(report, ["employee"])
        return report
    except IntegrityError:
        await db.rollback()
        raise BadRequestException


async def update_work_report_entity(
        report_id: int,
        data: WorkReportUpdateRequestSchema,
        db: AsyncSession
) -> None:
    # checking if ID is valid
    stmt = select(WorkReportModel).where(WorkReportModel.id == report_id)
    report = (await db.execute(stmt)).scalar_one_or_none()
    if report is None:
        raise NotFoundEntityException("Report with the given ID does not exist.")

    if data.employee_id:
        stmt = select(EmployeeModel).where(EmployeeModel.id == data.employee_id)
        employee = (await db.execute(stmt)).scalar_one_or_none()

        if employee is None:
            raise NotFoundEntityException("Employee with the given ID does not exist.")

    for field, value in data.model_dump(exclude_unset=True).items():
        print(f"DEBUG: setting {field}: {value}")
        setattr(report, field, value)

    # checking if update data conflicts with existing report (same day, same employee)
    existing_report_stmt = select(WorkReportModel).where(
        and_(
            WorkReportModel.employee_id == report.employee_id,
            WorkReportModel.work_date == report.work_date,
        )
    )
    existing_same_reports = (await db.execute(existing_report_stmt)).scalars().all()
    if len(existing_same_reports) > 1:
        raise ConflictEntityException("Report for given date already exists for given employee.")

    try:
        await db.commit()
        await db.refresh(report, ["employee"])
    except IntegrityError:
        await db.rollback()
        raise BadRequestException
