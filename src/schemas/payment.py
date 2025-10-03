from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from schemas.payroll_run import SalaryLineDetailSchema


class PaymentCreateRequestSchema(BaseModel):
    employee_id: int
    salary_line_id: int | None = None
    payroll_run_id: int | None = None
    amount: Decimal
    paid_date: date
    method: str | None

    model_config = ConfigDict(from_attributes=True)


class PaymentDetailResponseSchema(BaseModel):
    id: int
    employee_id: int
    salary_line_id: int | None
    # salary_line_id: SalaryLineDetailSchema | None
    payroll_run_id: int | None
    amount: Decimal
    paid_date: date
    method: str | None

    model_config = ConfigDict(from_attributes=True)


class PaymentListItemResponseSchema(BaseModel):
    id: int
    employee_id: int
    amount: Decimal
    paid_date: date
    method: str | None

    model_config = ConfigDict(from_attributes=True)


class PaymentListResponseSchema(BaseModel):
    items: list[PaymentListItemResponseSchema] = Field(default_factory=list)
    total: int

    model_config = ConfigDict(from_attributes=True)
