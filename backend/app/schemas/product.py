from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    retailer_id: int = Field(
        gt=0,
    )

    category_id: int | None = Field(
        default=None,
        gt=0,
    )

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    sku: str = Field(
        min_length=1,
        max_length=100,
    )

    barcode: str | None = Field(
        default=None,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    cost_price: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    selling_price: Decimal = Field(
        ge=0,
        decimal_places=2,
    )

    unit: str = Field(
        min_length=1,
        max_length=30,
    )

    tax_rate: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        decimal_places=2,
    )


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: int | None = Field(
        default=None,
        gt=0,
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    sku: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    barcode: str | None = Field(
        default=None,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    cost_price: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
    )

    selling_price: Decimal | None = Field(
        default=None,
        ge=0,
        decimal_places=2,
    )

    unit: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    tax_rate: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        decimal_places=2,
    )

    is_active: bool | None = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool