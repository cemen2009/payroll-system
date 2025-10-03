from decimal import Decimal

from sqlalchemy import String, DECIMAL
from sqlalchemy.orm import Mapped, relationship, mapped_column

from models.base import BaseModel


class PositionModel(BaseModel):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    rate: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
        info={"tip": "Rate of an employee per hour"}
    )

    employees: Mapped[list["EmployeeModel"]] = relationship(
        "EmployeeModel",
        back_populates="position"
    )

    @classmethod
    def default_order_by(cls):
        return [cls.title.asc()]

    def __repr__(self) -> str:
        return f"<Position {self.title} [${self.rate}/hour]>"
