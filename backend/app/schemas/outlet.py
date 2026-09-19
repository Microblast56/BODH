from pydantic import BaseModel, ConfigDict, Field


class OutletCreate(BaseModel):
    restaurant_id: int
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=30)

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


class OutletUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
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


class OutletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    restaurant_id: int
    name: str
    code: str

    address_line1: str | None
    address_line2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str
    phone: str | None

    is_active: bool