from datetime import date

from pydantic import BaseModel, field_validator, ConfigDict

from schemas.employee import EmployeeBaseSchema


class VacationBaseSchema(BaseModel):
    start_date: date
    end_date: date
    employee_id: int

    @field_validator("end_date")
    def validate_end_date(cls, v: date, info) -> date:
        if v <= info.data["start_date"]:
            raise ValueError("Start date must be before end date")
        return v


class VacationDetailResponseSchema(BaseModel):
    id: int
    start_date: date
    end_date: date
    employee: EmployeeBaseSchema

    model_config = ConfigDict(from_attributes=True)


class VacationListItemResponseSchema(VacationBaseSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class VacationListResponseSchema(BaseModel):
    vacations: list[VacationListItemResponseSchema]
    total: int


class VacationCreateRequestSchema(VacationBaseSchema):
    pass


class VacationUpdateRequestSchema(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    employee_id: int | None = None

    @field_validator("end_date")
    def validate_end_date(cls, v: date | None, info) -> date | None:
        if v is not None and v <= info.data["start_date"]:
            raise ValueError("Start date must be before end date")
        return v
