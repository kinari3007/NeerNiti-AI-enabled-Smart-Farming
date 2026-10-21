"""
Neer Niti Smart Farming API — application entry point.

Startup sequence:
  1. Configure logging.
  2. Pre-load the ML model (so the first request is not slow).
  3. Create database tables (dev convenience; use Alembic in production).
  4. Seed reference data (crops, sample fertilizer products).
  5. Start serving requests.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi import HTTPException

from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.exceptions import (
    BusinessError,
    ExternalServiceError,
    NotFoundError,
    UnauthorizedError,
    business_error_handler,
    external_service_handler,
    http_exception_handler,
    not_found_handler,
    unauthorized_handler,
    unhandled_exception_handler,
    validation_error_handler,
)
from app.core.logging import configure_logging

logger = logging.getLogger("neerniti")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown."""
    configure_logging()
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Database: %s", settings.DATABASE_URL.split("@")[-1])  # hide credentials

    # Pre-load ML model (lazy-loaded, but warm it up now)
    from app.ml.model_loader import load_model
    pipeline, le, meta = load_model()
    if pipeline is not None:
        version = (meta or {}).get("model_version", "unknown")
        macro_f1 = (meta or {}).get("test_macro_f1", "unknown")
        logger.info("ML model loaded: version=%s test_macro_f1=%s", version, macro_f1)
    else:
        logger.warning(
            "ML model not available. Run ml/src/models/train_classifier.py to generate artifacts."
        )

    # Create DB tables (use Alembic for production migrations)
    from app.db.init_db import create_all_tables, seed_initial_data
    from app.db.session import AsyncSessionLocal
    await create_all_tables()

    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)

    logger.info("%s started successfully.", settings.APP_NAME)
    yield

    logger.info("%s shutting down.", settings.APP_NAME)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-enabled smart farming API for cost-optimised fertilizer recommendations.\n\n"
        "**Important disclaimers:**\n"
        "- The ML classifier predicts a fertilizer *category* — not validated nutrient quantities.\n"
        "- Nutrient requirements are approximate ICAR reference values, not field-calibrated.\n"
        "- Fertilizer prices may include illustrative sample values — check `is_verified` per record.\n"
        "- Always consult a certified agronomist for field-specific advice."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

app.add_exception_handler(NotFoundError, not_found_handler)        # type: ignore[arg-type]
app.add_exception_handler(BusinessError, business_error_handler)   # type: ignore[arg-type]
app.add_exception_handler(UnauthorizedError, unauthorized_handler) # type: ignore[arg-type]
app.add_exception_handler(ExternalServiceError, external_service_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(HTTPException, http_exception_handler)   # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health_router)    # /health, /health/db (no version prefix)
app.include_router(api_router)       # /api/v1/...
