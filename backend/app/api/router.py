"""
Central API router — mounts all versioned sub-routers.
"""
from fastapi import APIRouter

from app.api.routes import (
    crops,
    farms,
    fertilizers,
    recommendations,
    soil,
    weather,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(farms.router)
api_router.include_router(soil.router)
api_router.include_router(crops.router)
api_router.include_router(weather.router)
api_router.include_router(fertilizers.router)
api_router.include_router(recommendations.router)
