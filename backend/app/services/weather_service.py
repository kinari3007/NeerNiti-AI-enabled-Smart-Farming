"""
Weather service using Open-Meteo (https://open-meteo.com).

Open-Meteo is free and requires no API key.
Responses are cached in-memory by (lat, lon) rounded to 4 decimal places.
Cache TTL is configurable via WEATHER_CACHE_TTL_SECONDS.

Design guarantees:
  - Never fabricates weather values; returns None for missing fields.
  - Raises RuntimeError (caught by the recommendation service) on any failure.
  - Clearly distinguishes current (observed) from forecast data in the response.
  - Implements connection + read timeouts and does not block the event loop.
"""
import logging
import time
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.schemas.weather import WeatherCurrent, WeatherForecastDay, WeatherResponse

logger = logging.getLogger("neerniti.weather_service")

# Simple in-process LRU-style cache: {cache_key: (fetched_unix_ts, WeatherResponse)}
_weather_cache: dict[str, tuple[float, WeatherResponse]] = {}

_OPEN_METEO_CURRENT_VARS = (
    "temperature_2m,"
    "relative_humidity_2m,"
    "precipitation,"
    "wind_speed_10m,"
    "weather_code"
)
_OPEN_METEO_DAILY_VARS = (
    "temperature_2m_max,"
    "temperature_2m_min,"
    "precipitation_sum,"
    "precipitation_probability_max"
)


def _make_cache_key(latitude: float, longitude: float) -> str:
    return f"{latitude:.4f}_{longitude:.4f}"


def _get_cached(key: str) -> WeatherResponse | None:
    entry = _weather_cache.get(key)
    if entry is None:
        return None
    fetched_at, response = entry
    if time.time() - fetched_at < settings.WEATHER_CACHE_TTL_SECONDS:
        return response
    del _weather_cache[key]
    return None


def _put_cache(key: str, response: WeatherResponse) -> None:
    _weather_cache[key] = (time.time(), response)


async def get_weather_for_farm(
    farm_id: str,
    latitude: float,
    longitude: float,
) -> WeatherResponse:
    """
    Fetch current weather and 7-day forecast from Open-Meteo.
    Raises RuntimeError if coordinates are missing or the API is unavailable.
    """
    if latitude is None or longitude is None:
        raise RuntimeError(
            "Farm has no coordinates. Add latitude and longitude to the farm "
            "before requesting weather data."
        )

    cache_key = _make_cache_key(latitude, longitude)
    cached = _get_cached(cache_key)
    if cached is not None:
        logger.debug("Weather cache HIT for farm %s (%s)", farm_id, cache_key)
        return WeatherResponse(**{**cached.model_dump(), "is_cached": True})

    logger.debug("Weather cache MISS for farm %s — fetching from Open-Meteo", farm_id)

    params: dict = {
        "latitude": latitude,
        "longitude": longitude,
        "current": _OPEN_METEO_CURRENT_VARS,
        "daily": _OPEN_METEO_DAILY_VARS,
        "forecast_days": 7,
        "timezone": "auto",
    }

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)
        ) as client:
            response = await client.get(settings.WEATHER_API_BASE_URL, params=params)
            response.raise_for_status()
            data: dict = response.json()
    except httpx.TimeoutException as exc:
        logger.warning("Weather API timeout for farm %s: %s", farm_id, exc)
        raise RuntimeError(
            "The weather API request timed out. Try again later."
        ) from exc
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Weather API HTTP %s for farm %s: %s",
            exc.response.status_code, farm_id, exc,
        )
        raise RuntimeError(
            f"Weather API returned HTTP {exc.response.status_code}. Try again later."
        ) from exc
    except Exception as exc:
        logger.warning("Weather API unexpected error for farm %s: %s", farm_id, exc)
        raise RuntimeError(f"Weather data is currently unavailable: {exc}") from exc

    # --- Parse response ---
    current_raw = data.get("current", {})
    current = WeatherCurrent(
        temperature_2m=current_raw.get("temperature_2m"),
        relative_humidity_2m=current_raw.get("relative_humidity_2m"),
        precipitation=current_raw.get("precipitation"),
        wind_speed_10m=current_raw.get("wind_speed_10m"),
        weather_code=current_raw.get("weather_code"),
        time=current_raw.get("time"),
    )

    daily = data.get("daily", {})
    dates: list[str] = daily.get("time", [])
    n = len(dates)

    def _safe_list(key: str) -> list:
        return daily.get(key, [None] * n)

    forecast_days: list[WeatherForecastDay] = [
        WeatherForecastDay(
            date=dates[i],
            temperature_max=_safe_list("temperature_2m_max")[i],
            temperature_min=_safe_list("temperature_2m_min")[i],
            precipitation_sum=_safe_list("precipitation_sum")[i],
            precipitation_probability_max=_safe_list("precipitation_probability_max")[i],
        )
        for i in range(n)
    ]

    result = WeatherResponse(
        farm_id=farm_id,
        latitude=latitude,
        longitude=longitude,
        current=current,
        forecast_days=forecast_days,
        fetched_at=datetime.now(timezone.utc),
        is_cached=False,
    )

    _put_cache(cache_key, result)
    logger.info(
        "Weather fetched for farm %s (lat=%.4f, lon=%.4f)", farm_id, latitude, longitude
    )
    return result


def clear_weather_cache() -> None:
    """Clear the in-memory cache. Used in tests."""
    _weather_cache.clear()
