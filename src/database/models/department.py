from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.models.base import BaseModel


class DepartmentModel(BaseModel):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(255), unique=True)

    chief_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), unique=True)
    chief: Mapped["EmployeeModel"] = relationship(
        foreign_keys=[chief_id],
        # that's a kludge, because chief is also an employee, so it creates a cycle reference
        # we create object without chief, then we make one more UPDATE to insert a chief
        post_update=True
    )

    # chief is also in employees
    employees: Mapped[list["EmployeeModel"]] = relationship(
        back_populates="department",
        foreign_keys="EmployeeModel.department_id"
    )

    def __repr__(self) -> str:
        return f"<Department {self.name} (#{self.code})>"
