from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class StockMovement(Base, TimestampMixin):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    inventory_id: Mapped[int] = mapped_column(
        ForeignKey("inventories.id"),
        nullable=False,
        index=True,
    )

    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"),
        nullable=True,
        index=True,
    )

    movement_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    quantity_change: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reference_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    reference_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    inventory: Mapped["Inventory"] = relationship(
        back_populates="stock_movements",
    )

    employee: Mapped["Employee | None"] = relationship(
        back_populates="stock_movements",
    )