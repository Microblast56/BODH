from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StoreBase(BaseModel):
    retailer_id: int = Field(
        gt=0,
    )

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    code: str = Field(
        min_length=1,
        max_length=30,
    )

    address_line1: str | None = Field(
        default=None,
        max_length=255,
    )

    address_line2: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=20,
    )

    country: str = Field(
        default="India",
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    address_line1: str | None = Field(
        default=None,
        max_length=255,
    )

    address_line2: str | None = Field(
        default=None,
        max_length=255,
    )

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=20,
    )

    country: str | None = Field(
        default=None,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    is_active: bool | None = None


class StoreResponse(StoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool