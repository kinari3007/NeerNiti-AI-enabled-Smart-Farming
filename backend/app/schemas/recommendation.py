"""
Recommendation request and response schemas.

Important distinction (also enforced in the service layer):
  1. ML classifier output  — suggests a fertilizer *category* based on input features.
                             It does NOT determine nutrient quantities or application rates.
  2. Nutrient requirements — approximate reference values from agronomic literature (ICAR).
                             They are NOT field-calibrated. Soil-test corrections are noted.
  3. Optimized plan        — cost-minimizing combination of available products that meets
                             the nutrient requirements subject to linear constraints.

These three outputs are presented separately in the response and must not be conflated.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """
    Parameters needed to generate a fertilizer recommendation for a farm.
    Soil readings are loaded from the database; use soil_reading_ids to
    restrict to specific readings, or leave None to use all farm readings.
    """

    crop_selection_id: Optional[str] = Field(
        None,
        description=(
            "ID of an existing CropSelection on this farm. "
            "If provided, crop_name and growth_stage are taken from it."
        ),
    )
    # If no crop_selection_id, these two are required
    crop_name: Optional[str] = Field(None, max_length=100, examples=["Wheat"])
    growth_stage: Optional[str] = Field(None, max_length=50, examples=["Sowing"])

    area_ha: Optional[float] = Field(
        None, gt=0,
        description="Cultivated area in hectares. Used to scale total nutrient needs.",
        examples=[1.0],
    )
    soil_reading_ids: Optional[list[str]] = Field(
        None,
        description="Specific soil reading IDs to use. If None, all farm readings are used.",
    )
    use_weather: bool = Field(
        True,
        description="Whether to fetch current weather for the farm.",
    )
    allow_unverified_prices: bool = Field(
        False,
        description=(
            "If True, recommendations may use unverified or sample prices. "
            "The response will clearly indicate price provenance."
        ),
    )
    notes: Optional[str] = Field(None, max_length=1000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "crop_name": "Wheat",
                "growth_stage": "Sowing",
                "area_ha": 1.0,
                "use_weather": True,
                "allow_unverified_prices": False,
            }
        }
    }


class MLClassifierOutput(BaseModel):
    """
    Output from the fertilizer category classifier.
    This is a data-driven suggestion, NOT a validated agronomic prescription.
    """

    predicted_class: str
    confidence: Optional[float] = None
    top_classes: Optional[list[dict]] = None  # [{class: str, probability: float}]
    input_features_used: Optional[list[str]] = None
    disclaimer: str = (
        "The ML classifier suggests a fertilizer category based on statistical patterns "
        "in training data. It does NOT determine scientifically validated nutrient "
        "quantities, application rates, or field-specific requirements."
    )


class OptimizedFertilizerItem(BaseModel):
    """A single fertilizer product in the optimized plan."""

    product_id: str
    product_name: str
    quantity_kg_per_ha: float = Field(..., description="Quantity in kg per hectare.")
    quantity_kg_total: float = Field(..., description="Total quantity for the given area.")
    price_per_kg: float
    cost_per_ha: float
    cost_total: float
    currency: str
    price_source: str
    price_verified: bool
    price_record_id: str
    price_recorded_at: datetime
    # Nutrients delivered by this quantity (per hectare, consistent with requirements)
    n_supplied_kg_per_ha: float = Field(..., description="N delivered (kg/ha).")
    p_supplied_kg_per_ha: float = Field(
        ..., description="P₂O₅ delivered (kg/ha) — label convention."
    )
    k_supplied_kg_per_ha: float = Field(
        ..., description="K₂O delivered (kg/ha) — label convention."
    )


class NutrientBalance(BaseModel):
    """Nutrient requirement vs. supply comparison."""

    n_required_kg_per_ha: float
    p_required_kg_per_ha: float
    k_required_kg_per_ha: float
    n_supplied_kg_per_ha: float
    p_supplied_kg_per_ha: float
    k_supplied_kg_per_ha: float
    n_deficit_kg_per_ha: float
    p_deficit_kg_per_ha: float
    k_deficit_kg_per_ha: float
    unit_convention: str = "N in elemental kg/ha; P as P₂O₅ kg/ha; K as K₂O kg/ha"


class RecommendationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    farm_id: str
    crop_selection_id: Optional[str]

    # --- Section 1: ML classifier output ---
    ml_classifier_suggestion: Optional[MLClassifierOutput] = None

    # --- Section 2: Agronomic nutrient requirements ---
    nutrient_requirements: Optional[dict] = Field(
        None,
        description="N/P/K requirements in kg/ha from the reference table.",
    )
    nutrient_requirement_source: Optional[str] = Field(
        None,
        description="Citation/provenance of the nutrient requirement values.",
    )

    # --- Section 3: Cost-optimized fertilizer plan ---
    optimization_status: str = Field(
        ...,
        description=(
            "One of: feasible, infeasible, skipped_no_requirements, "
            "skipped_no_prices, pending, error."
        ),
    )
    recommended_fertilizers: Optional[list[OptimizedFertilizerItem]] = None
    nutrient_balance: Optional[NutrientBalance] = None
    estimated_total_cost: Optional[float] = None
    cost_currency: Optional[str] = None

    warnings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    created_at: datetime
