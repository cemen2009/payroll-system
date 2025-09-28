from datetime import date

from pydantic import BaseModel, ConfigDict

from schemas.common import (
    PositionListItemSchema,
    DepartmentListItemSchema,
    EmployeeListItemSchema
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


class EmployeeDetailResponseSchema(EmployeeBaseSchema):
    department: DepartmentListItemSchema | None
    position: PositionListItemSchema

    # vacations: list[VacationListItemSchema]
    # work_reports: list[WorkReportListItemSchema]
    # salary_reports: list[SalaryReportsListItemSchema]

    model_config = ConfigDict(from_attributes=True)


class EmployeeListResponseSchema(BaseModel):
    employees: list[EmployeeListItemSchema]
    next_page: str | None
    previous_page: str | None
    total_employees: int
    total_pages: int


class EmployeeCreateSchema(EmployeeBaseSchema):
    department_id: int | None
    position_id: int


class EmployeeUpdateSchema(EmployeeBaseSchema):
    department_id: int | None
    position_id: int
