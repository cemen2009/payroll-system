from decimal import Decimal

from sqlalchemy import ForeignKey, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class SalaryLineModel(BaseModel):
    __tablename__ = "salary_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    payroll_run_id: Mapped[int] = mapped_column(ForeignKey("payroll_runs.id"), nullable=False)

    gross_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    net_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    penalty_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=0)

    notes: Mapped[str | None]

    employee: Mapped["EmployeeModel"] = relationship("EmployeeModel", back_populates="salary_reports")
    payroll_run: Mapped["PayrollRunModel"] = relationship("PayrollRunModel", back_populates="salary_lines")

    @classmethod
    def default_order_by(cls):
        return [cls.employee_id]

    def __repr__(self):
        return f"<SalaryLine emp={self.employee_id} gross={self.gross_amount}>"