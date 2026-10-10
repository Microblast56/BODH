from sqlalchemy import ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import ActiveMixin, TimestampMixin


class Category(Base, TimestampMixin, ActiveMixin):
    __tablename__ = "categories"

    __table_args__ = (
        Index(
            "uq_categories_retailer_name",
            "retailer_id",
            "name",
            unique=True,
            postgresql_where=text("is_active IS TRUE"),
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

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    retailer: Mapped["Retailer"] = relationship(
        back_populates="categories",
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="category",
    )
