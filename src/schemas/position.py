from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from schemas.employee import EmployeeListItemSchema


class PositionBaseSchema(BaseModel):
    title: str
    rate: Decimal


class PositionDetailResponseSchema(PositionBaseSchema):
    id: int
    employees: list[EmployeeListItemSchema]

    model_config = ConfigDict(from_attributes=True)


class PositionListItemSchema(PositionBaseSchema):
    model_config = ConfigDict(from_attributes=True)


class PositionListResponseSchema(BaseModel):
    positions: list[PositionListItemSchema]
    previous_page: str | None
    next_page: str | None
    total_positions: int
    total_pages: int


class PositionCreateSchema(PositionBaseSchema):
    pass


class PositionUpdateSchema(PositionBaseSchema):
    pass
