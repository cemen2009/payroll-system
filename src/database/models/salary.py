from datetime import date
from decimal import Decimal

from sqlalchemy import Date, DECIMAL, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.models.base import BaseModel

class SalaryReportModel(BaseModel):
    __tablename__ = "salary_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    month: Mapped[date] = mapped_column(Date, info={"tip": "First date of a month"})
    base_salary: Mapped[Decimal] = mapped_column(DECIMAL)
    extra_salary: Mapped[Decimal] = mapped_column(DECIMAL)
    vacation_pay: Mapped[Decimal] = mapped_column(DECIMAL)
    tax: Mapped[Decimal] = mapped_column(DECIMAL, info={"tip": "20% of social tax"})
    net_salary: Mapped[Decimal] = mapped_column(DECIMAL)
    payment_date: Mapped[date] = mapped_column(Date)
    overdue_days: Mapped[int] = mapped_column(Integer)
    penalty: Mapped[Decimal] = mapped_column(DECIMAL, info={"tip": "0.1% of penalty per day"})

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    employee: Mapped["EmployeeModel"] = relationship(back_populates="salary_reports", foreign_keys=[employee_id])
