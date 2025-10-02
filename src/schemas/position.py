from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.common import PositionListItemResponseSchema, EmployeeListItemResponseSchema


class PositionBaseSchema(BaseModel):
    title: str
    rate: Decimal

    @field_validator("title")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title can not be empty.")
        return v

    @field_validator("rate")
    @classmethod
    def positive_rate(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Rate can not be negative.")
        return v


class PositionDetailResponseSchema(PositionBaseSchema):
    id: int
    employees: list[EmployeeListItemResponseSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class PositionListResponseSchema(BaseModel):
    positions: list[PositionListItemResponseSchema]
    total: int


class PositionCreateRequestSchema(PositionBaseSchema):
    pass


class PositionUpdateRequestSchema(BaseModel):
    title: str | None = None
    rate: Decimal | None = None
