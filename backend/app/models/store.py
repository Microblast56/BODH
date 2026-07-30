from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import ActiveMixin, TimestampMixin


class Store(Base, TimestampMixin, ActiveMixin):
    __tablename__ = "stores"

    __table_args__ = (
        UniqueConstraint(
            "retailer_id",
            "code",
            name="uq_stores_retailer_code",
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

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    address_line1: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address_line2: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    postal_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        default="India",
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    retailer: Mapped["Retailer"] = relationship(
        back_populates="stores",
    )

    employees: Mapped[list["Employee"]] = relationship(
    back_populates="store",
    )

    inventories: Mapped[list["Inventory"]] = relationship(
    back_populates="store",
    )