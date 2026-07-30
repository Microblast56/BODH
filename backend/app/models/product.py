from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import ActiveMixin, TimestampMixin


class Product(Base, TimestampMixin, ActiveMixin):
    __tablename__ = "products"

    __table_args__ = (
        UniqueConstraint(
            "retailer_id",
            "sku",
            name="uq_products_retailer_sku",
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

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    sku: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    barcode: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    selling_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="piece",
    )

    tax_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    retailer: Mapped["Retailer"] = relationship(
        back_populates="products",
    )

    category: Mapped["Category | None"] = relationship(
        back_populates="products",
    )

    supplier_links: Mapped[list["ProductSupplier"]] = relationship(
    back_populates="product",
    )