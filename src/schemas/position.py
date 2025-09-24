from decimal import Decimal

from pydantic import BaseModel

from schemas.employee import EmployeeListItemSchema


class PositionBaseSchema(BaseModel):
    title: str
    rate: Decimal
    employees: list[EmployeeListItemSchema]


class PositionDetailResponseModel(PositionBaseSchema):
    id: int
    employees: list[EmployeeListItemSchema]


class PositionListResponseSchema(BaseModel):
    positions: list[PositionDetailResponseModel]
    previous_page: str
    next_page: str
    total_positions: int
    total_pages: int


class PositionCreateSchema(PositionBaseSchema):
    pass


class PositionUpdateSchema(PositionBaseSchema):
    pass
