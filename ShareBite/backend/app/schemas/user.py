from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

PublicRole = Literal["donor", "receiver", "volunteer"]
NeedPriority = Literal["low", "medium", "high", "urgent"]


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: PublicRole = "receiver"  # Admin cannot be created through public registration.
    phone: str | None = Field(default=None, max_length=30)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    needed_quantity: float | None = Field(default=None, gt=0, le=100000)
    need_priority: NeedPriority = "medium"

    @model_validator(mode="after")
    def coordinates_are_a_pair(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be provided together")
        return self


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    phone: str | None
    latitude: float | None
    longitude: float | None
    needed_quantity: float | None
    need_priority: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
