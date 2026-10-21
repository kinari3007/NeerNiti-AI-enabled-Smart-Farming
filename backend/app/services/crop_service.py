"""
Crop reference catalogue and farm crop-selection service.
"""
import json
import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessError, NotFoundError
from app.models.crop import CropReference, CropSelection
from app.schemas.crop import CropSelectionCreate, CropSelectionResponse

logger = logging.getLogger("neerniti.crop_service")

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

_SEED_CROPS: list[dict] = [
    {
        "name": "Rice",
        "description": "Oryza sativa — staple cereal crop grown in flooded or upland conditions.",
        "typical_growth_stages": json.dumps(["Sowing", "Germination", "Vegetative", "Flowering", "Maturity", "Harvest"]),
    },
    {
        "name": "Wheat",
        "description": "Triticum aestivum — Rabi season cereal crop widely grown across India.",
        "typical_growth_stages": json.dumps(["Sowing", "Germination", "Vegetative", "Flowering", "Maturity", "Harvest"]),
    },
    {
        "name": "Maize",
        "description": "Zea mays — versatile cereal grown in Kharif and Rabi seasons.",
        "typical_growth_stages": json.dumps(["Sowing", "Vegetative", "Flowering", "Maturity", "Harvest"]),
    },
    {
        "name": "Cotton",
        "description": "Gossypium hirsutum — Kharif fibre crop, major commercial crop.",
        "typical_growth_stages": json.dumps(["Sowing", "Vegetative", "Flowering", "Maturity", "Harvest"]),
    },
    {
        "name": "Potato",
        "description": "Solanum tuberosum — short-duration tuber crop.",
        "typical_growth_stages": json.dumps(["Sowing", "Vegetative", "Flowering", "Maturity", "Harvest"]),
    },
    {
        "name": "Sugarcane",
        "description": "Saccharum officinarum — long-duration perennial cash crop.",
        "typical_growth_stages": json.dumps(["Sowing", "Germination", "Vegetative", "Flowering", "Maturity", "Harvest"]),
    },
    {
        "name": "Tomato",
        "description": "Solanum lycopersicum — high-value vegetable crop.",
        "typical_growth_stages": json.dumps(["Sowing", "Vegetative", "Flowering", "Maturity", "Harvest"]),
    },
    {
        "name": "Soybean",
        "description": "Glycine max — Kharif oilseed and protein crop.",
        "typical_growth_stages": json.dumps(["Sowing", "Vegetative", "Flowering", "Maturity", "Harvest"]),
    },
    {
        "name": "Groundnut",
        "description": "Arachis hypogaea — Kharif oilseed crop.",
        "typical_growth_stages": json.dumps(["Sowing", "Vegetative", "Flowering", "Maturity", "Harvest"]),
    },
    {
        "name": "Mustard",
        "description": "Brassica juncea — Rabi oilseed crop.",
        "typical_growth_stages": json.dumps(["Sowing", "Vegetative", "Flowering", "Maturity", "Harvest"]),
    },
]


async def seed_crop_references(db: AsyncSession) -> None:
    """Seed the crop reference catalogue if the table is empty."""
    count_result = await db.execute(select(func.count()).select_from(CropReference))
    count = count_result.scalar_one()
    if count > 0:
        logger.debug("Crop references already seeded (%d rows).", count)
        return

    for crop_data in _SEED_CROPS:
        db.add(CropReference(**crop_data))

    logger.info("Seeded %d crop references.", len(_SEED_CROPS))


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

async def list_crop_references(db: AsyncSession) -> list[CropReference]:
    result = await db.execute(
        select(CropReference)
        .where(CropReference.is_active == True)  # noqa: E712
        .order_by(CropReference.name)
    )
    return list(result.scalars().all())


async def get_crop_reference(db: AsyncSession, crop_id: str) -> CropReference:
    result = await db.execute(
        select(CropReference).where(CropReference.id == crop_id)
    )
    crop = result.scalar_one_or_none()
    if crop is None:
        raise NotFoundError("CropReference", crop_id)
    return crop


async def get_crop_reference_by_name(
    db: AsyncSession, name: str
) -> CropReference | None:
    result = await db.execute(
        select(CropReference).where(
            func.lower(CropReference.name) == name.lower()
        )
    )
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# Crop selections
# ---------------------------------------------------------------------------

async def create_crop_selection(
    db: AsyncSession, farm_id: str, data: CropSelectionCreate
) -> CropSelection:
    # Verify farm exists
    from app.models.farm import Farm
    farm_result = await db.execute(select(Farm).where(Farm.id == farm_id))
    if farm_result.scalar_one_or_none() is None:
        raise NotFoundError("Farm", farm_id)

    # Verify crop reference exists
    crop_ref = await get_crop_reference(db, data.crop_reference_id)

    selection = CropSelection(
        farm_id=farm_id,
        crop_reference_id=data.crop_reference_id,
        variety=data.variety,
        growth_stage=data.growth_stage,
        planting_date=data.planting_date,
        expected_area_value=data.expected_area_value,
        expected_area_unit=data.expected_area_unit,
        expected_yield_kg_per_ha=data.expected_yield_kg_per_ha,
        notes=data.notes,
    )
    db.add(selection)
    await db.commit()
    await db.refresh(selection)

    logger.info(
        "Created crop selection id=%s farm=%s crop=%s stage=%s",
        selection.id, farm_id, crop_ref.name, data.growth_stage,
    )
    return selection


async def get_crop_selection(
    db: AsyncSession, farm_id: str, selection_id: str
) -> CropSelection:
    result = await db.execute(
        select(CropSelection).where(
            CropSelection.id == selection_id,
            CropSelection.farm_id == farm_id,
        )
    )
    sel = result.scalar_one_or_none()
    if sel is None:
        raise NotFoundError("CropSelection", selection_id)
    return sel


def _to_crop_selection_response(sel: CropSelection, crop_name: str) -> CropSelectionResponse:
    return CropSelectionResponse(
        id=sel.id,
        farm_id=sel.farm_id,
        crop_reference_id=sel.crop_reference_id,
        crop_name=crop_name,
        variety=sel.variety,
        growth_stage=sel.growth_stage,
        planting_date=sel.planting_date,
        expected_area_value=sel.expected_area_value,
        expected_area_unit=sel.expected_area_unit,
        expected_yield_kg_per_ha=sel.expected_yield_kg_per_ha,
        notes=sel.notes,
        created_at=sel.created_at,
    )


async def list_crop_selections_for_farm(
    db: AsyncSession, farm_id: str
) -> list[CropSelectionResponse]:
    result = await db.execute(
        select(CropSelection, CropReference.name)
        .join(CropReference, CropSelection.crop_reference_id == CropReference.id)
        .where(CropSelection.farm_id == farm_id)
        .order_by(CropSelection.created_at.desc())
    )
    rows = result.all()
    return [_to_crop_selection_response(sel, name) for sel, name in rows]
