from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.common import DepartmentListItemResponseSchema
from schemas.employee import EmployeeBaseSchema


class DepartmentBaseSchema(BaseModel):
    name: str
    code: str

    @field_validator("name", "code")
    @classmethod
    def validate_nullability(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field ca not be empty.")
        return v


class DepartmentDetailResponseSchema(DepartmentBaseSchema):
    id: int
    chief: EmployeeBaseSchema | None
    employees: list[EmployeeBaseSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DepartmentListResponseSchema(BaseModel):
    departments: list[DepartmentListItemResponseSchema]
    total: int


class DepartmentCreateRequestSchema(DepartmentBaseSchema):
    chief_id: int | None


class DepartmentUpdateRequestSchema(BaseModel):
    name: str | None = None
    code: str | None = None
    chief_id: int | None = None
