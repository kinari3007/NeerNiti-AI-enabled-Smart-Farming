"""
Database initialisation helpers.

For production, use Alembic migrations instead of create_all.
create_all is provided here for local development convenience and tests.
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.db.session import engine

# Import all models so Base.metadata knows about them before create_all
from app.models import farm, soil_reading, crop, fertilizer, recommendation  # noqa: F401

logger = logging.getLogger("neerniti")


async def create_all_tables() -> None:
    """Create all tables that do not already exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (or already exist).")


async def seed_initial_data(session: AsyncSession) -> None:
    """
    Seed reference data (crop catalogue, fertilizer products).
    Import lazily to avoid circular imports.
    """
    from app.services.crop_service import seed_crop_references
    from app.services.fertilizer_service import seed_sample_products

    await seed_crop_references(session)
    await seed_sample_products(session)
    await session.commit()
    logger.info("Initial seed data applied.")
