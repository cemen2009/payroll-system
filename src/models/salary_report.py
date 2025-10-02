from datetime import date
from decimal import Decimal

from sqlalchemy import Date, DECIMAL, Integer, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import mapped_column, Mapped, relationship, validates

from models.base import BaseModel


class SalaryReportModel(BaseModel):
    __tablename__ = "salary_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    month: Mapped[date] = mapped_column(Date, info={"tip": "First date of a month"})
    base_salary: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    extra_salary: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    vacation_pay: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    payment_date: Mapped[date] = mapped_column(Date)
    overdue_days: Mapped[int] = mapped_column(Integer)

    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    employee: Mapped["EmployeeModel"] = relationship(back_populates="salary_reports", foreign_keys=[employee_id])

    __table_args__ = (
        # ensures data integrity at the database level, protects against bypassing Python code
        CheckConstraint("overdue_days >= 0", name="check_overdue_days_non_negative"),

        UniqueConstraint("employee_id", "month", name="unique_employee_month"),
    )

    @validates("month")
    def validate_month(self, key, value: date) -> date:
        if value.day != 1:
            raise ValueError("Month must be the first day a month (e.g. 2025-09-01)")
        return value

    # fast feedback, prevents bad values in Python objects. Python layer
    @validates("overdue_days")
    def validate_overdue_days(self, key, value: int) -> int:
        if value < 0:
            raise ValueError("Overdue days must be non-negative")
        return value

    @hybrid_property
    def gross(self) -> Decimal:
        return self.base_salary + self.extra_salary + self.vacation_pay

    @gross.expression
    def gross(cls):
        return cls.base_salary + cls.extra_salary + cls.vacation_pay

    @hybrid_property
    def tax(self) -> Decimal:
        """20% of (base + extra + vacation)"""
        return self.gross * Decimal("0.20")

    @tax.expression
    def tax(cls):
        return cls.gross * Decimal("0.20")

    @hybrid_property
    def net_salary(self) -> Decimal:
        """Total salary after tax"""
        return self.gross - self.tax

    @net_salary.expression
    def net_salary(cls):
        return cls.gross - cls.tax

    @hybrid_property
    def penalty(self) -> Decimal:
        """0.1% penalty per day, applied to net_salary"""
        return self.net_salary * Decimal("0.001") * self.overdue_days

    @penalty.expression
    def penalty(cls):
        return cls.net_salary * 0.001 * cls.overdue_days

    def __repr__(self):
        return f"<Salary Report of Employee #{self.employee_id} for {self.month}>"
