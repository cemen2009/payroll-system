from datetime import date

from sqlalchemy import Integer, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import BaseModel


class PayrollRunModel(BaseModel):
    __tablename__ = "payroll_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    generated_at: Mapped[date] = mapped_column(Date, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    paid_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    salary_lines: Mapped[list["SalaryLineModel"]] = relationship(
        "SalaryLineModel", back_populates="payroll_run", cascade="all, delete-orphan"
    )

    @classmethod
    def default_order_by(cls):
        return [cls.year.desc(), cls.month.desc()]

    def __repr__(self):
        return f"<PayrollRun {self.year}-{self.month:02d}>"