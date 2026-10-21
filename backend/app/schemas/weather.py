"""
Weather data schemas.

Observed (current) and forecast weather are clearly distinguished.
All values are Optional — missing data is surfaced, never fabricated.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WeatherCurrent(BaseModel):
    """Observed weather at the time of the API call."""

    temperature_2m: Optional[float] = Field(
        None, description="Air temperature at 2 m height (°C)."
    )
    relative_humidity_2m: Optional[float] = Field(
        None, description="Relative humidity at 2 m height (%)."
    )
    precipitation: Optional[float] = Field(
        None, description="Precipitation in the last hour (mm)."
    )
    wind_speed_10m: Optional[float] = Field(
        None, description="Wind speed at 10 m height (km/h)."
    )
    weather_code: Optional[int] = Field(
        None, description="WMO weather interpretation code."
    )
    # ISO 8601 string as returned by Open-Meteo
    time: Optional[str] = None


class WeatherForecastDay(BaseModel):
    """Single-day weather forecast."""

    date: str = Field(..., description="Forecast date (YYYY-MM-DD).")
    temperature_max: Optional[float] = Field(None, description="Max temperature (°C).")
    temperature_min: Optional[float] = Field(None, description="Min temperature (°C).")
    precipitation_sum: Optional[float] = Field(None, description="Total precipitation (mm).")
    precipitation_probability_max: Optional[int] = Field(
        None, description="Max precipitation probability (%)."
    )


class WeatherResponse(BaseModel):
    """
    Complete weather response for a farm.

    is_cached = True when the data was served from the in-memory cache
    rather than a live API call.
    """

    farm_id: str
    latitude: float
    longitude: float
    current: Optional[WeatherCurrent] = None
    forecast_days: list[WeatherForecastDay] = Field(default_factory=list)
    data_source: str = "Open-Meteo (https://open-meteo.com)"
    fetched_at: datetime
    is_cached: bool = False
    warning: Optional[str] = None
