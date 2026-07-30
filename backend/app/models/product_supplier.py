from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class ProductSupplier(Base, TimestampMixin):
    __tablename__ = "product_suppliers"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "supplier_id",
            name="uq_product_suppliers_product_supplier",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.id"),
        nullable=False,
        index=True,
    )

    supplier_product_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    purchase_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    is_preferred: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    product: Mapped["Product"] = relationship(
        back_populates="supplier_links",
    )

    supplier: Mapped["Supplier"] = relationship(
        back_populates="product_links",
    )