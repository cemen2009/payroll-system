from datetime import date
from typing import Optional

from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.models.base import BaseModel


class EmployeeModel(BaseModel):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tab_number: Mapped[int] = mapped_column(unique=True, info={
        "tip": "Unique tab number of an employee"
    })
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    middle_name: Mapped[str] = mapped_column(String(255), nullable=True)
    social_security_number: Mapped[int] = mapped_column(unique=True)
    birth_date: Mapped[date] = mapped_column(Date)
    address: Mapped[str] = mapped_column(String(255))
    hire_date: Mapped[date] = mapped_column(Date)
    termination_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=True)
    department: Mapped["DepartmentModel"] = relationship(
        back_populates="employees",
        foreign_keys=[department_id]
    )

    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"))
    position: Mapped["PositionModel"] = relationship(back_populates="employees")

    work_reports: Mapped[list["WorkReportModel"]] = relationship(back_populates="employee")

    salary_reports: Mapped[list["SalaryReportModel"]] = relationship(back_populates="employee")

    def __repr__(self) -> str:
        return f"Employee {self.first_name} {self.last_name} (#{self.tab_number})"
