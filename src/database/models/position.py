from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, relationship, mapped_column

from database.models.base import BaseModel


class PositionModel(BaseModel):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    rate: Mapped[float] = mapped_column(Float, nullable=False, info={"tip": "Rate of an employee per hour"})

    employees: Mapped[list["EmployeeModel"]] = relationship(back_populates="position")
