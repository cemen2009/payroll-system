from datetime import date

from pydantic import BaseModel, field_validator, ConfigDict

from models.work_report import WorkingDayType
from schemas import EmployeeListItemResponseSchema


class WorkReportBaseSchema(BaseModel):
    work_date: date
    day_type: WorkingDayType
    hours_worked: int

    @field_validator("hours_worked")
    def hours_worked_validator(cls, v: int) -> int:
        if v < 0 or v > 24:
            raise ValueError("Duration of working hours must be between 0 and 24")
        return v


class WorkReportListItemResponseSchema(WorkReportBaseSchema):
    id: int
    employee_id: int

    model_config = ConfigDict(from_attributes=True)


class WorkReportListResponseSchema(BaseModel):
    items: list[WorkReportListItemResponseSchema]
    total: int


class WorkReportDetailResponseSchema(WorkReportBaseSchema):
    id: int
    employee: EmployeeListItemResponseSchema

    model_config = ConfigDict(from_attributes=True)


class WorkReportCreateRequestSchema(WorkReportBaseSchema):
    employee_id: int


class WorkReportUpdateRequestSchema(BaseModel):
    work_date: date | None = None
    day_type: WorkingDayType | None = None
    hours_worked: int | None = None
    employee_id: int | None = None

    @field_validator("hours_worked")
    def hours_worked_validator(cls, v: int) -> int:
        if v < 0 or v > 24:
            raise ValueError("Duration of working hours must be between 0 and 24")
        return v
