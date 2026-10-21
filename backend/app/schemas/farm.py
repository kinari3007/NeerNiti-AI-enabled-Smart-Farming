"""
Farm request and response schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class FarmCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Green Valley Farm"])
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, examples=[28.6139])
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, examples=[77.2090])
    area_value: Optional[float] = Field(None, gt=0, examples=[2.5])
    area_unit: Optional[str] = Field(
        None,
        pattern="^(hectare|acre|sqm|bigha)$",
        examples=["hectare"],
    )
    location_description: Optional[str] = Field(
        None, max_length=500, examples=["Village Rampur, District Agra"]
    )
    # Irrigation water pH — optional; only used in recommendations when provided
    irrigation_water_ph: Optional[float] = Field(
        None, ge=0.0, le=14.0, examples=[7.2]
    )
    irrigation_water_ph_source: Optional[str] = Field(
        None, max_length=100, examples=["Manual measurement, pH meter"]
    )

    @model_validator(mode="after")
    def validate_coordinates_pair(self) -> "FarmCreate":
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError(
                "Both latitude and longitude must be provided together, or neither."
            )
        return self


class FarmUpdate(BaseModel):
    """All fields optional — PATCH semantics."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    area_value: Optional[float] = Field(None, gt=0)
    area_unit: Optional[str] = Field(None, pattern="^(hectare|acre|sqm|bigha)$")
    location_description: Optional[str] = Field(None, max_length=500)
    irrigation_water_ph: Optional[float] = Field(None, ge=0.0, le=14.0)
    irrigation_water_ph_source: Optional[str] = Field(None, max_length=100)

    @model_validator(mode="after")
    def validate_coordinates_pair(self) -> "FarmUpdate":
        lat_set = self.latitude is not None
        lon_set = self.longitude is not None
        if lat_set != lon_set:
            raise ValueError(
                "Both latitude and longitude must be provided together, or neither."
            )
        return self


class FarmResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    latitude: Optional[float]
    longitude: Optional[float]
    area_value: Optional[float]
    area_unit: Optional[str]
    location_description: Optional[str]
    irrigation_water_ph: Optional[float]
    irrigation_water_ph_source: Optional[str]
    irrigation_water_ph_timestamp: Optional[datetime]
    created_at: datetime
    updated_at: datetime
