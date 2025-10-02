from datetime import date
from enum import Enum

from sqlalchemy import Date, Integer, ForeignKey, CheckConstraint
from sqlalchemy import Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class WorkingDayType(str, Enum):
    WEEKDAY = "weekday"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"


class WorkReportModel(BaseModel):
    """
    Model for saving report of working time for each employee.
    """

    __tablename__ = "work_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    work_date: Mapped[date] = mapped_column(
        Date, nullable=False, info={"tip": "Report will be saved for this day"}
    )
    day_type: Mapped[WorkingDayType] = mapped_column(
        PgEnum(
            WorkingDayType,
            native_enum=False,
            values_callable=lambda enum: [e.value for e in enum],
            validate_strings=True
        ),
        nullable=False
    )
    hours_worked: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("hours_worked >= 0 AND hours_worked <= 24"),
        nullable=False
    )

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    employee: Mapped["EmployeeModel"] = relationship(
        "EmployeeModel", back_populates="work_reports", foreign_keys=[employee_id]
    )

    @classmethod
    def default_order_by(cls):
        return [cls.work_date.desc(), cls.hours_worked.desc()]

    def __repr__(self):
        return f"<Work Report of Employee #{self.employee_id} for {self.work_date}>"
