from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from sqlalchemy.orm import selectinload

from models import PayrollRunModel, SalaryLineModel, EmployeeModel, WorkReportModel
from exceptions import ConflictEntityException, NotFoundEntityException
from decimal import Decimal

from schemas import PayrollRunListItemSchema


async def create_payroll_run_entity(year: int, month: int, db: AsyncSession) -> PayrollRunModel:
    existing_stmt = select(PayrollRunModel).where(
        and_(PayrollRunModel.year == year, PayrollRunModel.month == month)
    )
    existing_run = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing_run:
        raise ConflictEntityException

    try:
        payroll_run = PayrollRunModel(
            year=year,
            month=month,
            generated_at=date.today(),
            approved=False,
            paid_at=None
        )
        db.add(payroll_run)
        await db.flush()  # get payroll_run.id for FK in SalaryLine

        employees_stmt = select(EmployeeModel).options(
            selectinload(EmployeeModel.position)
        ).where(
            or_(
                EmployeeModel.termination_date == None,
                EmployeeModel.termination_date > date(year, month, 1)
            )
        )
        employees_result = await db.execute(employees_stmt)
        employees = employees_result.scalars().all()

        salary_lines = []

        for employee in employees:
            # calculate working hours for whole month
            work_stmt = select(WorkReportModel).where(
                and_(
                    WorkReportModel.employee_id == employee.id,
                    WorkReportModel.work_date.between(
                        date(year, month, 1),
                        date(year, month, 31)
                    )
                )
            )
            work_result = await db.execute(work_stmt)
            work_reports = work_result.scalars().all()
            total_hours = sum(r.hours_worked for r in work_reports)

            # calculate gross, tax, net
            rate = employee.position.rate
            gross = Decimal(total_hours) * rate

            # TODO: extra_hours, vacations, penalty
            tax = gross * Decimal("0.20")
            net = gross - tax

            salary_line = SalaryLineModel(
                employee_id=employee.id,
                payroll_run_id=payroll_run.id,
                gross_amount=gross,
                tax_amount=tax,
                net_amount=net,
                penalty_amount=Decimal("0"),
                notes=None
            )
            salary_lines.append(salary_line)

        db.add_all(salary_lines)
        await db.commit()

        await db.refresh(payroll_run, ["salary_lines"])
        return payroll_run

    except IntegrityError:
        await db.rollback()
        raise ConflictEntityException


async def fetch_payroll_by_id(payroll_id: int, db: AsyncSession) -> PayrollRunModel:
    stmt = select(PayrollRunModel).options(
        selectinload(PayrollRunModel.salary_lines)
    ).where(PayrollRunModel.id == payroll_id)

    result = await db.execute(stmt)
    payroll = result.scalar_one_or_none()

    if payroll is None:
        raise NotFoundEntityException("Payroll run not found.")

    return payroll


async def fetch_payrolls(offset: int, limit: int, db: AsyncSession) -> list[PayrollRunListItemSchema]:
    order_by: list = PayrollRunModel.default_order_by()
    stmt = select(PayrollRunModel)

    if order_by:
        stmt = stmt.order_by(*order_by)

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    payrolls = result.scalars().all()

    payrolls_list = [PayrollRunListItemSchema.model_validate(payroll) for payroll in payrolls]
    return payrolls_list


async def approve_payroll_run_entity(payroll_id: int, db: AsyncSession) -> PayrollRunModel:
    stmt = select(PayrollRunModel).where(PayrollRunModel.id == payroll_id)
    payroll = (await db.execute(stmt)).scalar_one_or_none()

    if payroll is None:
        raise NotFoundEntityException

    if payroll.approved:
        raise ConflictEntityException

    payroll.approved = True

    try:
        await db.commit()
        await db.refresh(payroll, ["salary_lines"])
        return payroll
    except IntegrityError:
        await db.rollback()
        raise
