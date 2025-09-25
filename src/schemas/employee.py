from datetime import date

from pydantic import BaseModel


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


class EmployeeListItemSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    department: str | None

    # TODO: add amount of work&salary reports


class EmployeeDetailResponseSchema(BaseModel):
    id: int

    department: str | None
    position: str


class EmployeeCreateSchema(EmployeeBaseSchema):
    department_id: int | None
    position_id: int


class EmployeeUpdateSchema(EmployeeBaseSchema):
    department_id: int | None
    position_id: int
