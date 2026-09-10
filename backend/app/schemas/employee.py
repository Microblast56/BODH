from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeBase(BaseModel):
    retailer_id: int = Field(
        gt=0,
    )

    store_id: int | None = Field(
        default=None,
        gt=0,
    )

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=20,
    )

    role: str = Field(
        min_length=2,
        max_length=50,
    )


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    store_id: int | None = Field(
        default=None,
        gt=0,
    )

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

    role: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    is_active: bool | None = None


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool