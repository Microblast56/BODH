from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import ActiveMixin, TimestampMixin


class Retailer(Base, TimestampMixin, ActiveMixin):
    __tablename__ = "retailers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    stores: Mapped[list["Store"]] = relationship(
    back_populates="retailer",
    )

    employees: Mapped[list["Employee"]] = relationship(
    back_populates="retailer",
    )