from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, DECIMAL, Integer, ForeignKey, String, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class PaymentModel(BaseModel):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    salary_line_id: Mapped[Optional[int]] = mapped_column(ForeignKey("salary_lines.id"), nullable=True)
    payroll_run_id: Mapped[Optional[int]] = mapped_column(ForeignKey("payroll_runs.id"), nullable=True)

    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    paid_date: Mapped[date] = mapped_column(Date, nullable=False)
    method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # cash, bank transfer, etc.

    employee: Mapped["EmployeeModel"] = relationship("EmployeeModel", back_populates="payments")
    salary_line: Mapped[Optional["SalaryLineModel"]] = relationship("SalaryLineModel")
    payroll_run: Mapped[Optional["PayrollRunModel"]] = relationship("PayrollRunModel")

    __table_args__ = (
        CheckConstraint("amount >= 0", name="check_payment_amount_positive"),

        # rejects multiple payment of the same salary line for same employee
        UniqueConstraint("employee_id", "salary_line_id", name="uq_employee_salary_line_payment"),

        # rejects payments for the same period and date
        UniqueConstraint("employee_id", "payroll_run_id", "paid_date", name="uq_employee_payroll_date"),
    )

    @classmethod
    def default_order_by(cls):
        return [cls.paid_date.desc()]

    def __repr__(self):
        return f"<Payment emp={self.employee_id} amount={self.amount} date={self.paid_date}>"
