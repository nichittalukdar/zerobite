from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class DonationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    category: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=4000)
    photo_url: HttpUrl | None = None
    pickup_address: str | None = Field(default=None, max_length=500)
    quantity: float = Field(gt=0, le=100000)
    unit: str = Field(default="meals", min_length=1, max_length=30)
    expiry_at: datetime
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def coordinates_are_a_pair(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be provided together")
        return self


class DonationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=4000)
    photo_url: HttpUrl | None = None
    pickup_address: str | None = Field(default=None, max_length=500)
    quantity: float | None = Field(default=None, gt=0, le=100000)
    unit: str | None = Field(default=None, min_length=1, max_length=30)
    expiry_at: datetime | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class DonationPublic(BaseModel):
    id: int
    donor_id: int
    name: str
    category: str
    description: str | None
    photo_url: str | None
    pickup_address: str | None
    quantity: float
    unit: str
    expiry_at: datetime
    latitude: float | None
    longitude: float | None
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
