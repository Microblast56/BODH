from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RetailerBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=20,
    )


class RetailerCreate(RetailerBase):
    pass


class RetailerUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    is_active: bool | None = None


class RetailerResponse(RetailerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool