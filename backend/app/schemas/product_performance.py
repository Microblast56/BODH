from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductPerformanceItem(BaseModel):
    """Sales performance metrics for a single product."""

    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    sku: str
    retailer_id: int

    units_sold: int
    transaction_count: int

    total_revenue: Decimal
    average_selling_value_per_unit: Decimal


class ProductPerformanceResponse(BaseModel):
    """Product performance report for a selected scope and period."""

    model_config = ConfigDict(from_attributes=True)

    retailer_id: int | None
    store_id: int | None
    date_from: date | None
    date_to: date | None

    products: list[ProductPerformanceItem]
    total_products: int