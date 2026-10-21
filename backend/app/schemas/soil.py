"""
Soil reading request and response schemas.

Design principles:
- Every measurement field is optional. Not every sensor measures every parameter.
- Missing values must remain NULL; they must never be fabricated.
- Unit strings are validated at the schema layer to prevent mixed-unit aggregation.
- Out-of-range values are flagged (warnings), never silently rejected or altered.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

# Allowed unit strings
VALID_DATA_SOURCES = frozenset({"sensor", "manual", "import"})
VALID_EC_UNITS = frozenset({"dS/m", "mS/cm"})
VALID_MOISTURE_UNITS = frozenset({"%", "volumetric"})
VALID_NPK_UNITS = frozenset({"mg/kg", "kg/ha", "ppm"})
VALID_OC_UNITS = frozenset({"%", "g/kg"})


class SoilReadingCreate(BaseModel):
    collected_at: datetime = Field(..., description="Timestamp of sample collection (ISO 8601 with timezone).")

    # Sampling location within the farm (optional)
    sampling_latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    sampling_longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    sampling_location_description: Optional[str] = Field(None, max_length=255)

    # pH (dimensionless, 0–14)
    soil_ph: Optional[float] = Field(None, ge=0.0, le=14.0, description="Soil pH (0–14).")

    # Electrical conductivity
    electrical_conductivity: Optional[float] = Field(
        None, ge=0.0, le=20.0, description="EC value."
    )
    ec_unit: Optional[str] = Field(None, description="Unit for EC: 'dS/m' or 'mS/cm'.")

    # Moisture
    soil_moisture: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="Soil moisture value."
    )
    moisture_unit: Optional[str] = Field(
        None, description="Unit for moisture: '%' or 'volumetric'."
    )

    # NPK
    nitrogen: Optional[float] = Field(None, ge=0.0, le=10000.0)
    phosphorus: Optional[float] = Field(None, ge=0.0, le=10000.0)
    potassium: Optional[float] = Field(None, ge=0.0, le=10000.0)
    npk_unit: Optional[str] = Field(
        None, description="Unit for N, P, K: 'mg/kg', 'kg/ha', or 'ppm'."
    )

    # Organic carbon
    organic_carbon: Optional[float] = Field(None, ge=0.0, le=100.0)
    organic_carbon_unit: Optional[str] = Field(None, description="Unit: '%' or 'g/kg'.")

    # Metadata
    data_source: str = Field("manual", description="'sensor', 'manual', or 'import'.")
    sensor_id: Optional[str] = Field(None, max_length=100)

    @model_validator(mode="after")
    def _validate_all(self) -> "SoilReadingCreate":
        errors: list[str] = []

        if self.data_source not in VALID_DATA_SOURCES:
            errors.append(f"data_source must be one of {sorted(VALID_DATA_SOURCES)}.")

        if self.ec_unit is not None and self.ec_unit not in VALID_EC_UNITS:
            errors.append(f"ec_unit must be one of {sorted(VALID_EC_UNITS)}.")

        if self.moisture_unit is not None and self.moisture_unit not in VALID_MOISTURE_UNITS:
            errors.append(f"moisture_unit must be one of {sorted(VALID_MOISTURE_UNITS)}.")

        if self.npk_unit is not None and self.npk_unit not in VALID_NPK_UNITS:
            errors.append(f"npk_unit must be one of {sorted(VALID_NPK_UNITS)}.")

        if self.organic_carbon_unit is not None and self.organic_carbon_unit not in VALID_OC_UNITS:
            errors.append(f"organic_carbon_unit must be one of {sorted(VALID_OC_UNITS)}.")

        if (self.sampling_latitude is None) != (self.sampling_longitude is None):
            errors.append(
                "Both sampling_latitude and sampling_longitude must be provided together."
            )

        # If any NPK value is provided, a unit should be given
        npk_vals = [self.nitrogen, self.phosphorus, self.potassium]
        if any(v is not None for v in npk_vals) and self.npk_unit is None:
            errors.append("npk_unit is required when any N/P/K value is provided.")

        if self.electrical_conductivity is not None and self.ec_unit is None:
            errors.append("ec_unit is required when electrical_conductivity is provided.")

        if self.soil_moisture is not None and self.moisture_unit is None:
            errors.append("moisture_unit is required when soil_moisture is provided.")

        if errors:
            raise ValueError("; ".join(errors))

        return self


class SoilReadingResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    farm_id: str
    collected_at: datetime
    sampling_latitude: Optional[float]
    sampling_longitude: Optional[float]
    sampling_location_description: Optional[str]
    soil_ph: Optional[float]
    electrical_conductivity: Optional[float]
    ec_unit: Optional[str]
    soil_moisture: Optional[float]
    moisture_unit: Optional[str]
    nitrogen: Optional[float]
    phosphorus: Optional[float]
    potassium: Optional[float]
    npk_unit: Optional[str]
    organic_carbon: Optional[float]
    organic_carbon_unit: Optional[str]
    data_source: str
    sensor_id: Optional[str]
    is_validated: bool
    validation_flags: Optional[str]  # JSON string; parse client-side if needed
    created_at: datetime


class ParameterStats(BaseModel):
    """Descriptive statistics for a single numeric soil parameter."""

    count: int
    mean: float
    median: float
    min: float
    max: float
    std: Optional[float] = None  # None when count < 2
    unit: Optional[str] = None


class SoilSummaryResponse(BaseModel):
    """
    Aggregated statistics across all soil readings for a farm.
    Parameters absent from all readings have a None entry.
    """

    farm_id: str
    reading_count: int
    ph: Optional[ParameterStats] = None
    ec: Optional[ParameterStats] = None
    moisture: Optional[ParameterStats] = None
    nitrogen: Optional[ParameterStats] = None
    phosphorus: Optional[ParameterStats] = None
    potassium: Optional[ParameterStats] = None
    organic_carbon: Optional[ParameterStats] = None
    warnings: list[str] = Field(default_factory=list)
    unit_notes: list[str] = Field(default_factory=list)
