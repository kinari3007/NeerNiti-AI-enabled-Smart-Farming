"""
Weather endpoint.

GET /api/v1/farms/{farm_id}/weather
"""
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError
from app.db.session import get_db
from app.schemas.weather import WeatherResponse
from app.services.farm_service import get_farm
from app.services.weather_service import get_weather_for_farm

router = APIRouter(tags=["Weather"])
logger = logging.getLogger("neerniti.routes.weather")


@router.get(
    "/farms/{farm_id}/weather",
    response_model=WeatherResponse,
    summary="Current weather and forecast for a farm",
    description=(
        "Retrieves current conditions and 7-day forecast from Open-Meteo. "
        "Requires the farm to have latitude and longitude coordinates. "
        "Responses are cached for 30 minutes (configurable). "
        "Returns HTTP 422 if the farm has no coordinates."
    ),
)
async def get_farm_weather(
    farm_id: str,
    db: AsyncSession = Depends(get_db),
) -> WeatherResponse:
    farm = await get_farm(db, farm_id)

    if farm.latitude is None or farm.longitude is None:
        raise BusinessError(
            "Farm has no coordinates. "
            "Add latitude and longitude to retrieve weather data.",
            code="FARM_NO_COORDINATES",
        )

    try:
        return await get_weather_for_farm(farm_id, farm.latitude, farm.longitude)
    except RuntimeError as exc:
        # Surface weather errors with a clear message; do not expose stack trace
        raise BusinessError(str(exc), code="WEATHER_UNAVAILABLE") from exc
