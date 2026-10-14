from pydantic import BaseModel, ConfigDict


class LowStockItem(BaseModel):
    """Inventory item requiring attention."""

    model_config = ConfigDict(from_attributes=True)

    inventory_id: int
    retailer_id: int
    store_id: int
    store_name: str
    product_id: int
    product_name: str
    sku: str
    quantity_on_hand: int
    reorder_level: int
    reorder_quantity: int
    shortage_quantity: int


class LowStockReportResponse(BaseModel):
    """Low-stock inventory report for a selected scope."""

    model_config = ConfigDict(from_attributes=True)

    retailer_id: int | None
    store_id: int | None
    total_items: int
    items: list[LowStockItem]