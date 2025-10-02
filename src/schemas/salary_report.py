from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator

from schemas.employee import EmployeeBaseSchema


class SalaryReportBaseSchema(BaseModel):
    month: date
    base_salary: Decimal
    extra_salary: Decimal
    vacation_pay: Decimal
    payment_date: date
    overdue_days: int

    @field_validator("month")
    def month_validator(cls, v: date) -> date:
        if v.day != 1:
            raise ValueError("Month must be 1st day of the month")
        return v


class SalaryReportDetailResponseSchema(SalaryReportBaseSchema):
    id: int
    employee: EmployeeBaseSchema
    tax: Decimal
    net_salary: Decimal
    penalty: Decimal

    model_config = ConfigDict(from_attributes=True)


class SalaryReportListItemResponseSchema(BaseModel):
    net_salary: Decimal
    payment_date: date
    employee_id: int

    model_config = ConfigDict(from_attributes=True)


class SalaryReportListResponseSchema(BaseModel):
    items: list[SalaryReportListItemResponseSchema]
    total: int


class SalaryReportCreateRequestSchema(SalaryReportBaseSchema):
    employee_id: int


class SalaryReportUpdateRequestSchema(SalaryReportBaseSchema):
    month: date | None = None
    base_salary: Decimal | None = None
    extra_salary: Decimal | None = None
    vacation_pay: Decimal | None = None
    payment_date: date | None = None
    overdue_days: int | None = None
    employee_id: int | None = None

    @field_validator("month")
    def month_validator(cls, v: date) -> date:
        if v.day != 1:
            raise ValueError("Month must be 1st day of the month")
        return v
