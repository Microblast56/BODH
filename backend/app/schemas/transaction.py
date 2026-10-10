
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.transaction_item import (
    TransactionItemCreate,
    TransactionItemResponse,
)


class TransactionCreate(BaseModel):
    """Input for creating a sale."""

    retailer_id: int = Field(
        gt=0,
    )

    store_id: int = Field(
        gt=0,
    )

    employee_id: int | None = Field(
        default=None,
        gt=0,
    )

    transaction_number: str = Field(
        min_length=1,
        max_length=50,
    )

    payment_method: str = Field(
        min_length=2,
        max_length=30,
    )

    discount_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
        description="Discount applied to the entire transaction.",
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )

    items: list[TransactionItemCreate] = Field(
        min_length=1,
        description="At least one product line is required.",
    )


class TransactionResponse(BaseModel):
    """Persisted transaction with its sale lines."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    retailer_id: int
    store_id: int
    employee_id: int | None
    transaction_number: str
    status: str
    payment_method: str
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[TransactionItemResponse]
