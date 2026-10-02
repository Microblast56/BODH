from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StockMovementBase(BaseModel):
    inventory_id: int = Field(
        gt=0,
    )

    employee_id: int | None = Field(
        default=None,
        gt=0,
    )

    movement_type: str = Field(
        min_length=2,
        max_length=30,
    )

    quantity_change: int

    reference_type: str | None = Field(
        default=None,
        max_length=50,
    )

    reference_id: int | None = Field(
        default=None,
        gt=0,
    )

    notes: str | None = None


class StockMovementCreate(StockMovementBase):
    pass


class StockMovementUpdate(BaseModel):
    employee_id: int | None = Field(
        default=None,
        gt=0,
    )

    movement_type: str | None = Field(
        default=None,
        min_length=2,
        max_length=30,
    )

    quantity_change: int | None = None

    reference_type: str | None = Field(
        default=None,
        max_length=50,
    )

    reference_id: int | None = Field(
        default=None,
        gt=0,
    )

    notes: str | None = None


class StockMovementResponse(StockMovementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime