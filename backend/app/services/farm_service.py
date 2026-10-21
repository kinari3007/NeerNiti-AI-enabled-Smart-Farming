"""
Farm CRUD service.

All database access is async via SQLAlchemy 2.x.
Farm deletion is guarded: a farm with existing recommendations cannot be
deleted without first removing them, to protect data integrity.
"""
import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.farm import Farm
from app.models.recommendation import Recommendation
from app.schemas.farm import FarmCreate, FarmUpdate

logger = logging.getLogger("neerniti.farm_service")


async def create_farm(db: AsyncSession, data: FarmCreate) -> Farm:
    farm = Farm(
        name=data.name,
        latitude=data.latitude,
        longitude=data.longitude,
        area_value=data.area_value,
        area_unit=data.area_unit,
        location_description=data.location_description,
        irrigation_water_ph=data.irrigation_water_ph,
        irrigation_water_ph_source=data.irrigation_water_ph_source,
        irrigation_water_ph_timestamp=(
            datetime.now(timezone.utc) if data.irrigation_water_ph is not None else None
        ),
    )
    db.add(farm)
    await db.commit()
    await db.refresh(farm)
    logger.info("Created farm id=%s name=%r", farm.id, farm.name)
    return farm


async def get_farm(db: AsyncSession, farm_id: str) -> Farm:
    result = await db.execute(select(Farm).where(Farm.id == farm_id))
    farm = result.scalar_one_or_none()
    if farm is None:
        raise NotFoundError("Farm", farm_id)
    return farm


async def list_farms(
    db: AsyncSession, skip: int = 0, limit: int = 50
) -> tuple[list[Farm], int]:
    count_result = await db.execute(select(func.count()).select_from(Farm))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Farm).order_by(Farm.created_at.desc()).offset(skip).limit(limit)
    )
    farms = list(result.scalars().all())
    return farms, total


async def update_farm(db: AsyncSession, farm_id: str, data: FarmUpdate) -> Farm:
    farm = await get_farm(db, farm_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)

    # Refresh irrigation pH timestamp when pH value changes
    if "irrigation_water_ph" in update_data and update_data["irrigation_water_ph"] is not None:
        farm.irrigation_water_ph_timestamp = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(farm)
    logger.info("Updated farm id=%s", farm_id)
    return farm


async def delete_farm(db: AsyncSession, farm_id: str) -> None:
    farm = await get_farm(db, farm_id)

    # Guard: refuse deletion if recommendations exist
    rec_count_result = await db.execute(
        select(func.count()).select_from(Recommendation).where(
            Recommendation.farm_id == farm_id
        )
    )
    rec_count = rec_count_result.scalar_one()
    if rec_count > 0:
        raise BusinessError(
            f"Farm '{farm.name}' has {rec_count} existing recommendation(s). "
            "Delete all recommendations first, or archive the farm instead.",
            code="FARM_HAS_RECOMMENDATIONS",
        )

    await db.delete(farm)
    await db.commit()
    logger.info("Deleted farm id=%s", farm_id)
