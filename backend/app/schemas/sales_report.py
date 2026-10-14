from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SalesSummaryResponse(BaseModel):
    """Aggregated sales metrics for a selected scope and period."""

    model_config = ConfigDict(from_attributes=True)

    retailer_id: int | None
    store_id: int | None
    date_from: date | None
    date_to: date | None

    total_revenue: Decimal
    transaction_count: int
    average_transaction_value: Decimal
    units_sold: int