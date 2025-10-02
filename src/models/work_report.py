from datetime import date
from enum import Enum, auto

from sqlalchemy import Date, Integer, ForeignKey, CheckConstraint
from sqlalchemy import Enum as EnumType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class WorkingDayType(Enum):
    DEFAULT = auto()
    WEEKEND = auto()
    HOLIDAY = auto()


class WorkReportModel(BaseModel):
    """
    Model for saving report of working time for each employee.
    """

    __tablename__ = "work_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    work_date: Mapped[date] = mapped_column(
        Date, nullable=False, info={"tip": "Report will be saved for this day"}
    )
    day_type: Mapped[WorkingDayType] = mapped_column(EnumType(WorkingDayType), nullable=False)
    hours_worked: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("hours_worked >= 0 AND hours_worked <= 24"),
        nullable=False
    )

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    employee: Mapped["EmployeeModel"] = relationship(
        "EmployeeModel", back_populates="work_reports", foreign_keys=[employee_id]
    )

    def __repr__(self):
        return f"<Work Report of Employee #{self.employee_id} for {self.work_date}>"
