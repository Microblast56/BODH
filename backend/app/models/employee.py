from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import ActiveMixin, TimestampMixin


class Employee(Base, TimestampMixin, ActiveMixin):
    __tablename__ = "employees"

    __table_args__ = (
        UniqueConstraint(
            "retailer_id",
            "email",
            name="uq_employees_retailer_email",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    retailer_id: Mapped[int] = mapped_column(
        ForeignKey("retailers.id"),
        nullable=False,
        index=True,
    )

    store_id: Mapped[int | None] = mapped_column(
        ForeignKey("stores.id"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    retailer: Mapped["Retailer"] = relationship(
        back_populates="employees",
    )

    store: Mapped["Store | None"] = relationship(
        back_populates="employees",
    )

    stock_movements: Mapped[list["StockMovement"]] = relationship(
    back_populates="employee",
    )