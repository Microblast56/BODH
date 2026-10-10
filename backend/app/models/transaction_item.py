from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class TransactionItem(Base, TimestampMixin):
    __tablename__ = "transaction_items"

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_transaction_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_transaction_items_unit_price_non_negative",
        ),
        CheckConstraint(
            "discount_amount >= 0",
            name="ck_transaction_items_discount_non_negative",
        ),
        CheckConstraint(
            "tax_amount >= 0",
            name="ck_transaction_items_tax_non_negative",
        ),
        CheckConstraint(
            "line_total >= 0",
            name="ck_transaction_items_line_total_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    transaction_id: Mapped[int] = mapped_column(
        ForeignKey("transactions.id"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    line_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    transaction: Mapped["Transaction"] = relationship(
        back_populates="items",
    )

    product: Mapped["Product"] = relationship(
        back_populates="transaction_items",
    )