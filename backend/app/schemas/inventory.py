from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InventoryBase(BaseModel):
    store_id: int = Field(
        gt=0,
    )

    product_id: int = Field(
        gt=0,
    )

    quantity_on_hand: int = Field(
        default=0,
        ge=0,
    )

    reorder_level: int = Field(
        default=0,
        ge=0,
    )

    reorder_quantity: int = Field(
        default=0,
        ge=0,
    )

    last_restocked_at: datetime | None = None


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity_on_hand: int | None = Field(
        default=None,
        ge=0,
    )

    reorder_level: int | None = Field(
        default=None,
        ge=0,
    )

    reorder_quantity: int | None = Field(
        default=None,
        ge=0,
    )

    last_restocked_at: datetime | None = None


class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class StockAdjustmentBase(BaseModel):
    quantity: int = Field(
        gt=0,
    )

    employee_id: int | None = Field(
        default=None,
        gt=0,
    )

    reference_type: str | None = Field(
        default=None,
        max_length=50,
    )

    reference_id: int | None = Field(
        default=None,
        gt=0,
    )

    notes: str | None = None


class StockInCreate(StockAdjustmentBase):
    pass


class StockOutCreate(StockAdjustmentBase):
    pass