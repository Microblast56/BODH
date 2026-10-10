
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionItemCreate(BaseModel):
    """Input for one product line in a new sale."""

    product_id: int = Field(
        gt=0,
        description="ID of the product being sold.",
    )

    quantity: int = Field(
        gt=0,
        description="Number of units sold.",
    )

    discount_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        decimal_places=2,
        description="Total discount for this line, not per unit.",
    )


class TransactionItemResponse(BaseModel):
    """Persisted sale-line details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal
    created_at: datetime
    updated_at: datetime
