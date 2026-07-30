from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin


class Inventory(Base, TimestampMixin):
    __tablename__ = "inventories"

    __table_args__ = (
        UniqueConstraint(
            "store_id",
            "product_id",
            name="uq_inventories_store_product",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    quantity_on_hand: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    reorder_level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    reorder_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    last_restocked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    store: Mapped["Store"] = relationship(
        back_populates="inventories",
    )

    product: Mapped["Product"] = relationship(
        back_populates="inventories",
    )

    stock_movements: Mapped[list["StockMovement"]] = relationship(
    back_populates="inventory",
    )