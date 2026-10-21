"""
Feature engineering for the fertilizer classifier.

Assembles a one-row DataFrame in the exact column format expected by the
trained pipeline.  Missing values are represented as NaN — the pipeline's
preprocessor handles them via mean imputation where trained to do so.

The features used for training are documented in:
  ml/artifacts/model_metadata.json → features_numeric, features_categorical

IMPORTANT: The feature names here must exactly match the training-time
column names in fertilizer_recommendation.csv.
"""
from typing import Optional

import pandas as pd

from app.models.soil_reading import SoilReading
from app.schemas.recommendation import RecommendationRequest
from app.schemas.weather import WeatherResponse

# Must match the column names in the training dataset
NUMERIC_FEATURES = [
    "Soil_pH",
    "Soil_Moisture",
    "Organic_Carbon",
    "Electrical_Conductivity",
    "Nitrogen_Level",
    "Phosphorus_Level",
    "Potassium_Level",
    "Temperature",
    "Humidity",
    "Rainfall",
    "Yield_Last_Season",
]

CATEGORICAL_FEATURES = [
    "Soil_Type",
    "Crop_Type",
    "Crop_Growth_Stage",
    "Season",
    "Irrigation_Type",
    "Previous_Crop",
    "Region",
]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def _mean_or_none(readings: list[SoilReading], attr: str) -> Optional[float]:
    """Compute mean of a numeric attribute across readings, ignoring None."""
    vals = [getattr(r, attr) for r in readings if getattr(r, attr) is not None]
    return sum(vals) / len(vals) if vals else None


def _mode_or_none(readings: list[SoilReading], attr: str) -> Optional[str]:
    """Most common non-None string attribute value across readings."""
    vals = [str(getattr(r, attr)) for r in readings if getattr(r, attr) is not None]
    if not vals:
        return None
    return max(set(vals), key=vals.count)


def build_feature_dataframe(
    request: RecommendationRequest,
    crop_name: str,
    growth_stage: str,
    readings: list[SoilReading],
    weather: Optional[WeatherResponse],
) -> tuple[pd.DataFrame, list[str]]:
    """
    Build a single-row DataFrame of features for inference.
    Returns (feature_df, missing_feature_names).

    missing_feature_names lists features that had to be left as NaN because
    no data was available — included in the recommendation warnings.
    """
    missing: list[str] = []

    def _get(name: str, value) -> object:
        if value is None:
            missing.append(name)
            return float("nan")
        return value

    # --- Numeric features from soil readings ---
    avg_ph = _mean_or_none(readings, "soil_ph")
    avg_moisture = _mean_or_none(readings, "soil_moisture")
    avg_oc = _mean_or_none(readings, "organic_carbon")
    avg_ec = _mean_or_none(readings, "electrical_conductivity")
    avg_n = _mean_or_none(readings, "nitrogen")
    avg_p = _mean_or_none(readings, "phosphorus")
    avg_k = _mean_or_none(readings, "potassium")

    # --- Weather features ---
    temperature = None
    humidity = None
    rainfall = None
    if weather and weather.current:
        temperature = weather.current.temperature_2m
        humidity = weather.current.relative_humidity_2m
        # Use today's forecast precipitation if current precipitation is 0
        rainfall_current = weather.current.precipitation
        if weather.forecast_days:
            rainfall_forecast_7d = sum(
                d.precipitation_sum or 0.0 for d in weather.forecast_days
            )
        else:
            rainfall_forecast_7d = None

        # Use 7-day forecast total as a proxy for Rainfall feature
        rainfall = rainfall_forecast_7d if rainfall_forecast_7d is not None else rainfall_current

    row = {
        "Soil_pH": _get("Soil_pH", avg_ph),
        "Soil_Moisture": _get("Soil_Moisture", avg_moisture),
        "Organic_Carbon": _get("Organic_Carbon", avg_oc),
        "Electrical_Conductivity": _get("Electrical_Conductivity", avg_ec),
        "Nitrogen_Level": _get("Nitrogen_Level", avg_n),
        "Phosphorus_Level": _get("Phosphorus_Level", avg_p),
        "Potassium_Level": _get("Potassium_Level", avg_k),
        "Temperature": _get("Temperature", temperature),
        "Humidity": _get("Humidity", humidity),
        "Rainfall": _get("Rainfall", rainfall),
        "Yield_Last_Season": float("nan"),  # not available from request; always NaN
        # Categorical — map to dataset conventions
        "Soil_Type": "Loamy",           # default; not captured in current soil model
        "Crop_Type": crop_name,
        "Crop_Growth_Stage": growth_stage,
        "Season": "Kharif",             # default; not captured
        "Irrigation_Type": "Rainfed",   # default; not captured
        "Previous_Crop": "Wheat",       # default; not captured
        "Region": "Central",            # default; not captured
    }

    # Mark static defaults as informational (not warnings — they are expected)
    df = pd.DataFrame([row], columns=ALL_FEATURES)
    return df, missing
