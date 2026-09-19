from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)


class RestaurantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None


class RestaurantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr | None
    phone: str | None
    is_active: bool