from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import ActiveMixin, TimestampMixin


class Supplier(Base, TimestampMixin, ActiveMixin):
    __tablename__ = "suppliers"

    __table_args__ = (
        UniqueConstraint(
            "retailer_id",
            "name",
            name="uq_suppliers_retailer_name",
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
        String(150),
        nullable=False,
    )

    contact_person: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    retailer: Mapped["Retailer"] = relationship(
        back_populates="suppliers",
    )

    product_links: Mapped[list["ProductSupplier"]] = relationship(
        back_populates="supplier",
    )