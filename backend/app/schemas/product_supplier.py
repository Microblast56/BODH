from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductSupplierBase(BaseModel):
    product_id: int = Field(
        gt=0,
    )

    supplier_id: int = Field(
        gt=0,
    )

    supplier_product_code: str | None = Field(
        default=None,
        max_length=100,
    )

    purchase_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    is_preferred: bool = False


class ProductSupplierCreate(ProductSupplierBase):
    pass


class ProductSupplierUpdate(BaseModel):
    supplier_product_code: str | None = Field(
        default=None,
        max_length=100,
    )

    purchase_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    is_preferred: bool | None = None


class ProductSupplierResponse(ProductSupplierBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    created_at: datetime
    updated_at: datetime