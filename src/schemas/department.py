from pydantic import BaseModel, ConfigDict

from schemas.common import EmployeeListItemSchema, DepartmentListItemSchema


class DepartmentBaseSchema(BaseModel):
    name: str
    code: str


class DepartmentDetailResponseSchema(DepartmentBaseSchema):
    id: int
    chief: EmployeeListItemSchema | None
    employees: list[EmployeeListItemSchema] = []

    model_config = ConfigDict(from_attributes=True)


class DepartmentListResponseSchema(BaseModel):
    departments: list[DepartmentListItemSchema]
    total_departments: int
    total_pages: int
    next_page: str | None
    previous_page: str | None


class DepartmentCreateSchema(DepartmentBaseSchema):
    chief_id: int | None
