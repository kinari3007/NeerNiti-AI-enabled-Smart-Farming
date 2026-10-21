"""
Fertilizer product and price endpoints.

Public (read-only):
  GET  /api/v1/fertilizers
  GET  /api/v1/fertilizers/{fertilizer_id}
  GET  /api/v1/fertilizers/prices

Admin (require X-API-Key header):
  POST /api/v1/fertilizers
  POST /api/v1/fertilizers/prices/import
"""
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin_key
from app.db.session import get_db
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.fertilizer import (
    FertilizerPriceResponse,
    FertilizerProductCreate,
    FertilizerProductResponse,
    PriceImportResult,
)
from app.services import fertilizer_service

router = APIRouter(prefix="/fertilizers", tags=["Fertilizers"])

_PRICE_DISCLAIMER = (
    "Prices shown may include illustrative sample values that are NOT verified "
    "current market prices. Check the 'source' and 'is_verified' fields on each "
    "price record before making purchasing decisions."
)


@router.get(
    "",
    response_model=PaginatedResponse[FertilizerProductResponse],
    summary="List fertilizer products",
)
async def list_fertilizers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    active_only: bool = Query(True, description="Only return active products."),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[FertilizerProductResponse]:
    skip = (page - 1) * page_size
    products, total = await fertilizer_service.list_fertilizers(
        db, skip=skip, limit=page_size, active_only=active_only
    )
    return PaginatedResponse(
        items=[FertilizerProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/prices",
    response_model=list[FertilizerPriceResponse],
    summary="List fertilizer prices",
    description=_PRICE_DISCLAIMER,
)
async def list_prices(
    product_id: str | None = Query(None, description="Filter by product ID."),
    verified_only: bool = Query(
        False, description="Only return verified prices."
    ),
    db: AsyncSession = Depends(get_db),
) -> list[FertilizerPriceResponse]:
    prices = await fertilizer_service.list_prices(
        db, product_id=product_id, verified_only=verified_only
    )
    return [FertilizerPriceResponse.model_validate(p) for p in prices]


@router.get(
    "/{fertilizer_id}",
    response_model=FertilizerProductResponse,
    summary="Get a fertilizer product by ID",
)
async def get_fertilizer(
    fertilizer_id: str,
    db: AsyncSession = Depends(get_db),
) -> FertilizerProductResponse:
    product = await fertilizer_service.get_fertilizer(db, fertilizer_id)
    return FertilizerProductResponse.model_validate(product)


# ---------------------------------------------------------------------------
# Admin endpoints — protected by API key
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=FertilizerProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a fertilizer product (admin)",
    description=(
        "Requires `X-API-Key` header matching ADMIN_API_KEY environment variable. "
        "Nutrient percentages follow label convention: phosphorus as % P₂O₅, "
        "potassium as % K₂O, unless nutrient_as_elemental=true."
    ),
    dependencies=[Depends(require_admin_key)],
)
async def create_fertilizer(
    data: FertilizerProductCreate,
    db: AsyncSession = Depends(get_db),
) -> FertilizerProductResponse:
    product = await fertilizer_service.create_fertilizer(db, data)
    return FertilizerProductResponse.model_validate(product)


@router.post(
    "/prices/import",
    response_model=PriceImportResult,
    status_code=status.HTTP_200_OK,
    summary="Import fertilizer prices from CSV (admin)",
    description=(
        "Requires `X-API-Key` header. "
        "CSV must have a header row with columns: "
        "product_name, price_value, currency, price_unit. "
        "Optional columns: supplier, location, source, is_verified, bag_weight_kg. "
        "Products not found in the database are skipped (not created). "
        "Use source='verified_market' and is_verified=true only for confirmed prices."
    ),
    dependencies=[Depends(require_admin_key)],
)
async def import_prices(
    file: UploadFile = File(..., description="CSV file with price data."),
    db: AsyncSession = Depends(get_db),
) -> PriceImportResult:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        from app.core.exceptions import BusinessError
        raise BusinessError(
            "Only CSV files are accepted.", code="INVALID_FILE_TYPE"
        )
    content = await file.read()
    # Limit to 5 MB to prevent DoS via large uploads
    if len(content) > 5 * 1024 * 1024:
        from app.core.exceptions import BusinessError
        raise BusinessError(
            "File exceeds the 5 MB size limit.", code="FILE_TOO_LARGE"
        )
    return await fertilizer_service.import_prices_from_csv(db, content)
