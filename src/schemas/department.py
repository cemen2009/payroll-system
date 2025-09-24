from pydantic import BaseModel

from schemas.employee import EmployeeListItemSchema


class DepartmentBaseSchema(BaseModel):
    name: str


class DepartmentDetailResponseSchema(BaseModel):
    id: int
    chief: EmployeeListItemSchema
