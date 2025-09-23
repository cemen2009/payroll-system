from decimal import Decimal

from pydantic import BaseModel


class PositionBaseSchema(BaseModel):
    name: str
    rate: Decimal


class PositionDetailResponseModel(PositionBaseSchema):
    id: int


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
