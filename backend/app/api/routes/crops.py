"""
Crop reference catalogue and farm crop-selection endpoints.

GET  /api/v1/crops
GET  /api/v1/crops/{crop_id}
POST /api/v1/farms/{farm_id}/crop-selections
GET  /api/v1/farms/{farm_id}/crop-selections
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.crop import CropReferenceResponse, CropSelectionCreate, CropSelectionResponse
from app.services import crop_service

router = APIRouter(tags=["Crops"])


@router.get(
    "/crops",
    response_model=list[CropReferenceResponse],
    summary="List supported crops",
)
async def list_crops(
    db: AsyncSession = Depends(get_db),
) -> list[CropReferenceResponse]:
    crops = await crop_service.list_crop_references(db)
    return [CropReferenceResponse.model_validate(c) for c in crops]


@router.get(
    "/crops/{crop_id}",
    response_model=CropReferenceResponse,
    summary="Get a crop reference by ID",
)
async def get_crop(
    crop_id: str,
    db: AsyncSession = Depends(get_db),
) -> CropReferenceResponse:
    crop = await crop_service.get_crop_reference(db, crop_id)
    return CropReferenceResponse.model_validate(crop)


@router.post(
    "/farms/{farm_id}/crop-selections",
    response_model=CropSelectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a crop growing on a farm",
)
async def create_crop_selection(
    farm_id: str,
    data: CropSelectionCreate,
    db: AsyncSession = Depends(get_db),
) -> CropSelectionResponse:
    selection = await crop_service.create_crop_selection(db, farm_id, data)
    # Load crop name for response
    crop_ref = await crop_service.get_crop_reference(db, selection.crop_reference_id)
    return CropSelectionResponse(
        id=selection.id,
        farm_id=selection.farm_id,
        crop_reference_id=selection.crop_reference_id,
        crop_name=crop_ref.name,
        variety=selection.variety,
        growth_stage=selection.growth_stage,
        planting_date=selection.planting_date,
        expected_area_value=selection.expected_area_value,
        expected_area_unit=selection.expected_area_unit,
        expected_yield_kg_per_ha=selection.expected_yield_kg_per_ha,
        notes=selection.notes,
        created_at=selection.created_at,
    )


@router.get(
    "/farms/{farm_id}/crop-selections",
    response_model=list[CropSelectionResponse],
    summary="List crop selections for a farm",
)
async def list_crop_selections(
    farm_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[CropSelectionResponse]:
    return await crop_service.list_crop_selections_for_farm(db, farm_id)
