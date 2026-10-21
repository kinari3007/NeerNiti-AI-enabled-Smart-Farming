"""
Recommendation endpoints.

POST /api/v1/farms/{farm_id}/recommendations
GET  /api/v1/farms/{farm_id}/recommendations
GET  /api/v1/recommendations/{recommendation_id}
"""
import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import (
    create_recommendation,
    get_recommendation,
    list_recommendations,
    recommendation_to_response,
)

router = APIRouter(tags=["Recommendations"])
logger = logging.getLogger("neerniti.routes.recommendations")


@router.post(
    "/farms/{farm_id}/recommendations",
    response_model=RecommendationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a fertilizer recommendation for a farm",
    description=(
        "Runs the full recommendation pipeline:\n"
        "1. Loads the farm and its soil readings.\n"
        "2. Fetches weather (optional; requires farm coordinates).\n"
        "3. Runs the ML classifier for a fertilizer category suggestion.\n"
        "4. Looks up crop nutrient requirements from the ICAR reference table.\n"
        "5. Runs a cost-minimising LP optimizer over available fertilizer products.\n\n"
        "The response clearly separates:\n"
        "- **ml_classifier_suggestion**: statistical category prediction (not a prescription).\n"
        "- **nutrient_requirements**: approximate reference values (not field-calibrated).\n"
        "- **recommended_fertilizers**: LP-optimised plan with costs and nutrient balance.\n\n"
        "Set `allow_unverified_prices=true` to include unverified or sample prices "
        "(response will flag this clearly)."
    ),
)
async def generate_recommendation(
    farm_id: str,
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    rec = await create_recommendation(db, farm_id, request)
    return recommendation_to_response(rec)


@router.get(
    "/farms/{farm_id}/recommendations",
    response_model=list[RecommendationResponse],
    summary="List recommendations for a farm",
)
async def list_farm_recommendations(
    farm_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[RecommendationResponse]:
    recs = await list_recommendations(db, farm_id)
    return [recommendation_to_response(r) for r in recs]


@router.get(
    "/recommendations/{recommendation_id}",
    response_model=RecommendationResponse,
    summary="Get a recommendation by ID",
)
async def get_recommendation_by_id(
    recommendation_id: str,
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    rec = await get_recommendation(db, recommendation_id)
    return recommendation_to_response(rec)
