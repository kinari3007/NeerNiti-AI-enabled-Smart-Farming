"""
Fertilizer product and price schemas.

Nutrient accounting note (mirrored from the model):
  nitrogen_pct   = % elemental N
  phosphorus_pct = % P₂O₅  (label convention; default)
  potassium_pct  = % K₂O   (label convention; default)
  nutrient_as_elemental = True → phosphorus_pct and potassium_pct are elemental P% and K%
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

VALID_PRICE_SOURCES = frozenset({
    "user_entered",
    "csv_import",
    "verified_market",
    "illustrative_sample",
})
VALID_PRICE_UNITS = frozenset({
    "INR/kg", "INR/bag", "INR/tonne",
    "USD/kg", "USD/bag",
})


class FertilizerProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, examples=["Urea"])
    manufacturer: Optional[str] = Field(None, max_length=200)
    supplier: Optional[str] = Field(None, max_length=200)

    nitrogen_pct: float = Field(0.0, ge=0.0, le=100.0, examples=[46.0])
    phosphorus_pct: float = Field(0.0, ge=0.0, le=100.0, examples=[0.0])
    potassium_pct: float = Field(0.0, ge=0.0, le=100.0, examples=[0.0])
    nutrient_as_elemental: bool = Field(
        False,
        description=(
            "If False (default): phosphorus_pct is % P₂O₅, potassium_pct is % K₂O. "
            "If True: both are elemental %. The API converts internally."
        ),
    )
    nutrient_basis_note: Optional[str] = Field(None, max_length=500)

    product_form: Optional[str] = Field(
        None, max_length=50, examples=["granular"]
    )
    application_notes: Optional[str] = Field(None, max_length=1000)
    is_active: bool = True

    @model_validator(mode="after")
    def _check_nutrient_sum(self) -> "FertilizerProductCreate":
        total = self.nitrogen_pct + self.phosphorus_pct + self.potassium_pct
        if total > 100.0:
            raise ValueError(
                f"Sum of N + P + K percentages ({total:.1f}%) exceeds 100%. "
                "Please verify the nutrient composition."
            )
        return self


class FertilizerProductResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    manufacturer: Optional[str]
    supplier: Optional[str]
    nitrogen_pct: float
    phosphorus_pct: float
    potassium_pct: float
    nutrient_as_elemental: bool
    nutrient_basis_note: Optional[str]
    product_form: Optional[str]
    application_notes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class FertilizerPriceCreate(BaseModel):
    product_id: str
    price_value: float = Field(..., gt=0, examples=[280.0])
    currency: str = Field("INR", max_length=10, examples=["INR"])
    price_unit: str = Field("INR/kg", max_length=30, examples=["INR/kg"])
    bag_weight_kg: Optional[float] = Field(
        None, gt=0,
        description="Required when price_unit is per-bag (e.g. 'INR/bag').",
        examples=[50.0],
    )
    supplier: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200, examples=["Agra, Uttar Pradesh"])
    source: str = Field(
        "user_entered",
        description=f"Price provenance. One of: {sorted(VALID_PRICE_SOURCES)}",
    )
    is_verified: bool = False
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

    @model_validator(mode="after")
    def _validate(self) -> "FertilizerPriceCreate":
        errors: list[str] = []

        if self.source not in VALID_PRICE_SOURCES:
            errors.append(
                f"source must be one of {sorted(VALID_PRICE_SOURCES)}."
            )

        if "bag" in self.price_unit.lower() and self.bag_weight_kg is None:
            errors.append("bag_weight_kg is required when price_unit is per-bag.")

        if (
            self.valid_from is not None
            and self.valid_until is not None
            and self.valid_until <= self.valid_from
        ):
            errors.append("valid_until must be after valid_from.")

        if errors:
            raise ValueError("; ".join(errors))

        return self


class FertilizerPriceResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    product_id: str
    price_value: float
    currency: str
    price_unit: str
    bag_weight_kg: Optional[float]
    supplier: Optional[str]
    location: Optional[str]
    source: str
    is_verified: bool
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    verified_at: Optional[datetime]
    created_at: datetime


class PriceImportResult(BaseModel):
    imported: int
    skipped: int
    errors: list[str]
