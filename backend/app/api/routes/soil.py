"""
Soil reading endpoints.

POST /api/v1/farms/{farm_id}/soil-readings
GET  /api/v1/farms/{farm_id}/soil-readings
GET  /api/v1/farms/{farm_id}/soil-summary
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.soil import SoilReadingCreate, SoilReadingResponse, SoilSummaryResponse
from app.services import soil_service

router = APIRouter(tags=["Soil"])


@router.post(
    "/farms/{farm_id}/soil-readings",
    response_model=SoilReadingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a soil reading for a farm",
    description=(
        "Accepts a soil measurement from manual entry, sensor ingestion, or import. "
        "All measurement fields are optional — only provide what was actually measured. "
        "Missing values are stored as NULL, never fabricated. "
        "Readings outside typical agronomic ranges are flagged but not rejected."
    ),
)
async def create_soil_reading(
    farm_id: str,
    data: SoilReadingCreate,
    db: AsyncSession = Depends(get_db),
) -> SoilReadingResponse:
    reading = await soil_service.create_soil_reading(db, farm_id, data)
    return SoilReadingResponse.model_validate(reading)


@router.get(
    "/farms/{farm_id}/soil-readings",
    response_model=list[SoilReadingResponse],
    summary="List soil readings for a farm",
)
async def list_soil_readings(
    farm_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[SoilReadingResponse]:
    readings = await soil_service.list_soil_readings(db, farm_id)
    return [SoilReadingResponse.model_validate(r) for r in readings]


@router.get(
    "/farms/{farm_id}/soil-summary",
    response_model=SoilSummaryResponse,
    summary="Aggregate soil statistics for a farm",
    description=(
        "Computes descriptive statistics (mean, median, min, max, std) across all "
        "soil readings for this farm. Parameters with mixed units are excluded from "
        "aggregation and reported in unit_notes."
    ),
)
async def get_soil_summary(
    farm_id: str,
    db: AsyncSession = Depends(get_db),
) -> SoilSummaryResponse:
    return await soil_service.get_soil_summary(db, farm_id)
