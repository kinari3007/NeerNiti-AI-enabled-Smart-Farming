"""
Farm management endpoints.

POST   /api/v1/farms
GET    /api/v1/farms
GET    /api/v1/farms/{farm_id}
PATCH  /api/v1/farms/{farm_id}
DELETE /api/v1/farms/{farm_id}
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.farm import FarmCreate, FarmResponse, FarmUpdate
from app.services import farm_service

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post(
    "",
    response_model=FarmResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new farm",
)
async def create_farm(
    data: FarmCreate,
    db: AsyncSession = Depends(get_db),
) -> FarmResponse:
    farm = await farm_service.create_farm(db, data)
    return FarmResponse.model_validate(farm)


@router.get(
    "",
    response_model=PaginatedResponse[FarmResponse],
    summary="List all farms",
)
async def list_farms(
    page: int = Query(1, ge=1, description="Page number (1-indexed)."),
    page_size: int = Query(20, ge=1, le=100, description="Results per page."),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[FarmResponse]:
    skip = (page - 1) * page_size
    farms, total = await farm_service.list_farms(db, skip=skip, limit=page_size)
    return PaginatedResponse(
        items=[FarmResponse.model_validate(f) for f in farms],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Get a farm by ID",
)
async def get_farm(
    farm_id: str,
    db: AsyncSession = Depends(get_db),
) -> FarmResponse:
    farm = await farm_service.get_farm(db, farm_id)
    return FarmResponse.model_validate(farm)


@router.patch(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Partially update a farm",
)
async def update_farm(
    farm_id: str,
    data: FarmUpdate,
    db: AsyncSession = Depends(get_db),
) -> FarmResponse:
    farm = await farm_service.update_farm(db, farm_id, data)
    return FarmResponse.model_validate(farm)


@router.delete(
    "/{farm_id}",
    response_model=MessageResponse,
    summary="Delete a farm",
    description=(
        "Deletes a farm and all associated soil readings and crop selections. "
        "Fails if the farm has existing recommendations — delete them first."
    ),
)
async def delete_farm(
    farm_id: str,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    await farm_service.delete_farm(db, farm_id)
    return MessageResponse(message=f"Farm '{farm_id}' deleted successfully.")
