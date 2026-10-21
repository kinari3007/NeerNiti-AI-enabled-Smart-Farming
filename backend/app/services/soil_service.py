"""
Soil reading service.

Responsibilities:
  - Persist soil readings (manual entry, sensor, or import).
  - Validate each reading and attach agronomic flags (never silently alter values).
  - Compute descriptive statistics across multiple readings for a farm.
  - Warn when readings have incompatible units; refuse to aggregate them.

Missing measurement values stay NULL — they are never replaced with fabricated data.
"""
import json
import logging
from typing import Optional

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.models.soil_reading import SoilReading
from app.schemas.soil import (
    ParameterStats,
    SoilReadingCreate,
    SoilReadingResponse,
    SoilSummaryResponse,
)

logger = logging.getLogger("neerniti.soil_service")


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_and_flag(data: SoilReadingCreate) -> tuple[bool, list[str]]:
    """
    Check reading values against agronomic reference ranges.
    Returns (is_validated, list_of_flag_strings).
    is_validated = True only when the list is empty.
    Values are NEVER modified; flags are informational only.
    """
    flags: list[str] = []

    if data.soil_ph is not None:
        if data.soil_ph < settings.SOIL_PH_AGRONOMIC_MIN or data.soil_ph > settings.SOIL_PH_AGRONOMIC_MAX:
            flags.append(
                f"pH {data.soil_ph:.2f} is outside the typical agronomic range "
                f"({settings.SOIL_PH_AGRONOMIC_MIN}–{settings.SOIL_PH_AGRONOMIC_MAX}). "
                "Verify instrument calibration."
            )

    if data.electrical_conductivity is not None:
        if data.electrical_conductivity > settings.SOIL_EC_HIGH_THRESHOLD:
            flags.append(
                f"EC {data.electrical_conductivity} {data.ec_unit or 'dS/m'} exceeds "
                f"{settings.SOIL_EC_HIGH_THRESHOLD} dS/m — may indicate salinity stress."
            )

    if data.nitrogen is not None and data.nitrogen > settings.SOIL_N_HIGH_THRESHOLD:
        flags.append(
            f"Nitrogen reading ({data.nitrogen} {data.npk_unit or 'mg/kg'}) is unusually high "
            f"(threshold: {settings.SOIL_N_HIGH_THRESHOLD}). Verify sensor / lab result."
        )

    if data.soil_moisture is not None:
        if data.soil_moisture < 0 or data.soil_moisture > 100:
            flags.append(
                f"Moisture value {data.soil_moisture} is outside valid range 0–100%."
            )

    return (len(flags) == 0), flags


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

async def create_soil_reading(
    db: AsyncSession, farm_id: str, data: SoilReadingCreate
) -> SoilReading:
    # Ensure farm exists — raises NotFoundError if missing
    from app.models.farm import Farm
    farm_result = await db.execute(select(Farm).where(Farm.id == farm_id))
    if farm_result.scalar_one_or_none() is None:
        raise NotFoundError("Farm", farm_id)

    is_validated, flags = _validate_and_flag(data)

    reading = SoilReading(
        farm_id=farm_id,
        collected_at=data.collected_at,
        sampling_latitude=data.sampling_latitude,
        sampling_longitude=data.sampling_longitude,
        sampling_location_description=data.sampling_location_description,
        soil_ph=data.soil_ph,
        electrical_conductivity=data.electrical_conductivity,
        ec_unit=data.ec_unit,
        soil_moisture=data.soil_moisture,
        moisture_unit=data.moisture_unit,
        nitrogen=data.nitrogen,
        phosphorus=data.phosphorus,
        potassium=data.potassium,
        npk_unit=data.npk_unit,
        organic_carbon=data.organic_carbon,
        organic_carbon_unit=data.organic_carbon_unit,
        data_source=data.data_source,
        sensor_id=data.sensor_id,
        is_validated=is_validated,
        validation_flags=json.dumps(flags) if flags else None,
    )
    db.add(reading)
    await db.commit()
    await db.refresh(reading)

    if flags:
        logger.warning(
            "Soil reading id=%s for farm %s flagged: %s", reading.id, farm_id, flags
        )
    else:
        logger.info("Created soil reading id=%s for farm %s", reading.id, farm_id)

    return reading


async def list_soil_readings(
    db: AsyncSession, farm_id: str
) -> list[SoilReading]:
    # Verify farm exists
    from app.models.farm import Farm
    farm_result = await db.execute(select(Farm).where(Farm.id == farm_id))
    if farm_result.scalar_one_or_none() is None:
        raise NotFoundError("Farm", farm_id)

    result = await db.execute(
        select(SoilReading)
        .where(SoilReading.farm_id == farm_id)
        .order_by(SoilReading.collected_at.desc())
    )
    return list(result.scalars().all())


async def get_soil_reading(
    db: AsyncSession, farm_id: str, reading_id: str
) -> SoilReading:
    result = await db.execute(
        select(SoilReading).where(
            SoilReading.id == reading_id,
            SoilReading.farm_id == farm_id,
        )
    )
    reading = result.scalar_one_or_none()
    if reading is None:
        raise NotFoundError("SoilReading", reading_id)
    return reading


# ---------------------------------------------------------------------------
# Aggregation / summary
# ---------------------------------------------------------------------------

def _compute_stats(
    values: list[float], unit: Optional[str]
) -> Optional[ParameterStats]:
    """Compute descriptive statistics for a list of numeric values."""
    if not values:
        return None
    arr = np.array(values, dtype=float)
    return ParameterStats(
        count=len(arr),
        mean=float(np.mean(arr)),
        median=float(np.median(arr)),
        min=float(np.min(arr)),
        max=float(np.max(arr)),
        std=float(np.std(arr, ddof=1)) if len(arr) >= 2 else None,
        unit=unit,
    )


def _extract_numeric(
    readings: list[SoilReading],
    attr: str,
    unit_attr: Optional[str] = None,
) -> tuple[list[float], Optional[str], list[str]]:
    """
    Extract non-None values for a parameter from a list of readings.
    Returns (values, unit, unit_warnings).
    Warns — but does NOT aggregate — if readings have different units.
    """
    values: list[float] = []
    units: set[str] = set()
    warnings: list[str] = []

    for r in readings:
        val = getattr(r, attr, None)
        if val is not None:
            values.append(float(val))
            if unit_attr:
                unit_val = getattr(r, unit_attr, None)
                if unit_val is not None:
                    units.add(unit_val)

    if len(units) > 1:
        warnings.append(
            f"Readings for '{attr}' have mixed units {units}. "
            "Aggregation skipped to avoid unit mismatch. "
            "Re-submit readings with a consistent unit."
        )
        return [], None, warnings

    unit = next(iter(units)) if units else None
    return values, unit, warnings


async def get_soil_summary(
    db: AsyncSession, farm_id: str
) -> SoilSummaryResponse:
    readings = await list_soil_readings(db, farm_id)

    all_warnings: list[str] = []
    all_unit_notes: list[str] = []

    def _summarise(attr: str, unit_attr: Optional[str] = None) -> Optional[ParameterStats]:
        vals, unit, warns = _extract_numeric(readings, attr, unit_attr)
        if warns:
            all_unit_notes.extend(warns)
            return None
        return _compute_stats(vals, unit)

    # pH has no unit
    ph_vals = [float(r.soil_ph) for r in readings if r.soil_ph is not None]
    ph_stats = _compute_stats(ph_vals, None) if ph_vals else None

    ec_stats = _summarise("electrical_conductivity", "ec_unit")
    moisture_stats = _summarise("soil_moisture", "moisture_unit")
    n_stats = _summarise("nitrogen", "npk_unit")
    p_stats = _summarise("phosphorus", "npk_unit")
    k_stats = _summarise("potassium", "npk_unit")
    oc_stats = _summarise("organic_carbon", "organic_carbon_unit")

    # Collect validation flags from individual readings
    flagged = [r for r in readings if not r.is_validated and r.validation_flags]
    if flagged:
        all_warnings.append(
            f"{len(flagged)} reading(s) have validation flags. "
            "Review individual readings for details."
        )

    if not readings:
        all_warnings.append("No soil readings found for this farm.")

    return SoilSummaryResponse(
        farm_id=farm_id,
        reading_count=len(readings),
        ph=ph_stats,
        ec=ec_stats,
        moisture=moisture_stats,
        nitrogen=n_stats,
        phosphorus=p_stats,
        potassium=k_stats,
        organic_carbon=oc_stats,
        warnings=all_warnings,
        unit_notes=all_unit_notes,
    )
