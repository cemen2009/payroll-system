from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator

from schemas.common import (
    PositionListItemResponseSchema,
    DepartmentListItemResponseSchema,
    EmployeeListItemResponseSchema
)


class EmployeeBaseSchema(BaseModel):
    tab_number: int
    first_name: str
    last_name: str
    middle_name: str
    social_security_number: int
    birth_date: date
    address: str
    hire_date: date
    termination_date: date | None

    @field_validator("termination_date")
    @classmethod
    def validate_termination_date(cls, v: date | None, info) -> date | None:
        if v is not None and v < info.data["hire_date"]:
            raise ValueError("Hire date must be before termination date")
        return v


class EmployeeDetailResponseSchema(EmployeeBaseSchema):
    department: DepartmentListItemResponseSchema | None
    position: PositionListItemResponseSchema

    # vacations: list[VacationListItemSchema]
    # work_reports: list[WorkReportListItemSchema]
    # salary_reports: list[SalaryReportsListItemSchema]

    model_config = ConfigDict(from_attributes=True)


class EmployeeListResponseSchema(BaseModel):
    employees: list[EmployeeListItemResponseSchema]
    total: int


class EmployeeCreateRequestSchema(EmployeeBaseSchema):
    department_id: int | None
    position_id: int


class EmployeeUpdateRequestSchema(BaseModel):
    tab_number: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    social_security_number: int | None = None
    birth_date: date | None = None
    address: str | None = None
    hire_date: date | None = None
    termination_date: date | None = None

    department_id: int | None = None
    position_id: int | None = None
