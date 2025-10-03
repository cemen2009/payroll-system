from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SalaryLineDetailSchema(BaseModel):
    employee_id: int
    gross_amount: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    penalty_amount: Decimal | None = 0
    notes: str | None

    model_config = ConfigDict(from_attributes=True)


class PayrollRunDetailResponseSchema(BaseModel):
    id: int
    year: int
    month: int
    generated_at: date
    approved: bool
    paid_at: date | None
    salary_lines: list[SalaryLineDetailSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PayrollRunListItemSchema(BaseModel):
    id: int
    year: int
    month: int
    generated_at: date
    approved: bool
    paid_at: date | None

    model_config = ConfigDict(from_attributes=True)


class PayrollRunListResponseSchema(BaseModel):
    items: list[PayrollRunListItemSchema]
    total: int
