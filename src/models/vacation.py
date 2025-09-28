from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from models.base import BaseModel


if TYPE_CHECKING:
    from models.employee import EmployeeModel


class VacationModel(BaseModel):
    __tablename__ = "vacations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    employee: Mapped["EmployeeModel"] = relationship("EmployeeModel", back_populates="vacations")

    @property
    def duration(self):
        return self.end_date - self.start_date

    def __repr__(self):
        return f"<Vacation for {self.employee} [{self.duration} days]>"
