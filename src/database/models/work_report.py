from datetime import date
from enum import Enum, auto

from sqlalchemy import Date, Integer, ForeignKey
from sqlalchemy import Enum as EnumType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import BaseModel


class WorkingDayType(Enum):
    DEFAULT = auto()
    WEEKEND = auto()
    HOLIDAY = auto()


class WorkReportModel(BaseModel):
    """
    Model for saving report of working time for each employee.
    """

    __tablename__ = "work_reports"

    id: Mapped[int] = mapped_column(primary_key=True, auto_increment=True)
    work_date: Mapped[date] = mapped_column(Date, info={"tip": "Report will be saved for this day"})
    day_type: Mapped[WorkingDayType] = mapped_column(EnumType(WorkingDayType))
    hours_worked: Mapped[int] = mapped_column(Integer)

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    employee: Mapped["EmployeeModel"] = relationship(back_populates="work_reports", foreign_keys=[employee_id])
