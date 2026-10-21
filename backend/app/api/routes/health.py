"""
Health check endpoint.

GET /health   — liveness probe (always returns 200 if the process is alive)
GET /health/db — database connectivity check
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.ml.model_loader import is_model_available

router = APIRouter(tags=["Health"])
logger = logging.getLogger("neerniti.routes.health")


@router.get("/health", summary="Liveness probe")
async def health() -> dict:
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/health/db", summary="Database connectivity check")
async def health_db(db: AsyncSession = Depends(get_db)) -> dict:
    db_ok = False
    db_error: str | None = None
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        db_error = str(exc)
        logger.warning("Health DB check failed: %s", exc)

    ml_available = is_model_available()

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else f"error: {db_error}",
        "ml_model": "loaded" if ml_available else "not loaded (run training script)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
