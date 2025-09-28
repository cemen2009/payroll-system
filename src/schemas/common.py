from datetime import date
from decimal import Decimal

from pydantic import ConfigDict, BaseModel


class PositionListItemSchema(BaseModel):
    id: int
    title: str
    rate: Decimal

    model_config = ConfigDict(from_attributes=True)


class DepartmentListItemSchema(BaseModel):
    id: int
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class EmployeeListItemSchema(BaseModel):
    id: int
    tab_number: int
    first_name: str
    last_name: str
    termination_date: date | None

    department: DepartmentListItemSchema | None
    position: PositionListItemSchema

    model_config = ConfigDict(from_attributes=True)