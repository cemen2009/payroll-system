# this file was created to avoid circular import

from datetime import date
from decimal import Decimal

from pydantic import ConfigDict, BaseModel


class PositionListItemResponseSchema(BaseModel):
    id: int
    title: str
    rate: Decimal

    model_config = ConfigDict(from_attributes=True)


class DepartmentListItemResponseSchema(BaseModel):
    id: int
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class EmployeeListItemResponseSchema(BaseModel):
    id: int
    tab_number: int
    first_name: str
    last_name: str
    termination_date: date | None

    department: DepartmentListItemResponseSchema | None
    position: PositionListItemResponseSchema

    model_config = ConfigDict(from_attributes=True)