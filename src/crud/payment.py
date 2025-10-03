from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import PaymentModel, EmployeeModel, SalaryLineModel, PayrollRunModel
from exceptions import NotFoundEntityException, ConflictEntityException, BadRequestException
from schemas import PaymentCreateRequestSchema, PaymentListItemResponseSchema, PaymentDetailResponseSchema


async def create_payment_entity(data: PaymentCreateRequestSchema, db: AsyncSession) -> PaymentModel:
    employee = (await db.execute(
        select(EmployeeModel).where(EmployeeModel.id == data.employee_id)
    )).scalar_one_or_none()
    if employee is None:
        raise NotFoundEntityException(f"Employee with id={data.employee_id} not found")

    if data.salary_line_id is not None:
        salary_line = (await db.execute(
            select(SalaryLineModel).where(SalaryLineModel.id == data.salary_line_id)
        )).scalar_one_or_none()
        if salary_line is None:
            raise NotFoundEntityException(f"SalaryLine with id={data.salary_line_id} not found")

    if data.payroll_run_id is not None:
        payroll_run = (await db.execute(
            select(PayrollRunModel).where(PayrollRunModel.id == data.payroll_run_id)
        )).scalar_one_or_none()
        if payroll_run is None:
            raise NotFoundEntityException(f"PayrollRun with id={data.payroll_run_id} not found")

    payment = PaymentModel(**data.model_dump())

    try:
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return payment
    except IntegrityError as e:
        await db.rollback()

        # defining type of conflict by unique constraint names
        if "uq_employee_salary_line_payment" in str(e.orig):
            raise ConflictEntityException("Payment for this salary line and employee already exists.")
        if "uq_employee_payroll_date" in str(e.orig):
            raise ConflictEntityException("Payment for this employee, payroll run and date already exists.")
        raise BadRequestException(str(e))


async def fetch_payments(offset: int, limit: int, db: AsyncSession) -> list[PaymentListItemResponseSchema]:
    order_by = PaymentModel.default_order_by()
    stmt = select(PaymentModel)

    if order_by:
        stmt = stmt.order_by(*order_by)
    stmt = stmt.offset(offset).limit(limit)

    result = await db.execute(stmt)
    payments = result.scalars().all()

    return [PaymentListItemResponseSchema.model_validate(payment) for payment in payments]


async def fetch_payment_by_id(payment_id: int, db: AsyncSession) -> PaymentDetailResponseSchema:
    stmt = select(PaymentModel).options(
        selectinload(PaymentModel.salary_line),
    ).where(PaymentModel.id == payment_id)

    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()

    if payment is None:
        raise NotFoundEntityException(f"Payment with ID #{payment_id} was not found.")

    return PaymentDetailResponseSchema.model_validate(payment)
