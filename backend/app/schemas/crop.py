"""
Crop reference and crop selection schemas.
"""
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field

# Supported growth stages across all crops
VALID_GROWTH_STAGES = frozenset({
    "Sowing", "Germination", "Vegetative", "Flowering", "Maturity", "Harvest"
})


class CropReferenceResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    description: Optional[str]
    typical_growth_stages: Optional[str]  # JSON-encoded list string
    is_active: bool


class CropSelectionCreate(BaseModel):
    crop_reference_id: str = Field(..., description="ID of the crop from the crop reference catalogue.")
    variety: Optional[str] = Field(None, max_length=100, examples=["HD-2967"])
    growth_stage: str = Field(
        ...,
        description=f"Current growth stage. Valid values: {sorted(VALID_GROWTH_STAGES)}",
        examples=["Sowing"],
    )
    planting_date: Optional[date] = Field(None, examples=["2026-10-15"])
    expected_area_value: Optional[float] = Field(None, gt=0, examples=[2.5])
    expected_area_unit: Optional[str] = Field(
        None, pattern="^(hectare|acre|sqm|bigha)$", examples=["hectare"]
    )
    expected_yield_kg_per_ha: Optional[float] = Field(None, gt=0, examples=[4000.0])
    notes: Optional[str] = Field(None, max_length=1000)


class CropSelectionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    farm_id: str
    crop_reference_id: str
    crop_name: str  # populated by service layer from relationship
    variety: Optional[str]
    growth_stage: str
    planting_date: Optional[date]
    expected_area_value: Optional[float]
    expected_area_unit: Optional[str]
    expected_yield_kg_per_ha: Optional[float]
    notes: Optional[str]
    created_at: datetime
