"""
Shared pytest fixtures for the Neer Niti backend test suite.

All tests use an in-memory SQLite database via aiosqlite.
External calls (weather API) are mocked — no live network access required.
"""
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Use StaticPool so all connections (including flush + commit) share the same
# in-memory SQLite database within a single test.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    Fresh in-memory database per test function.
    StaticPool ensures all operations share the same connection.
    """
    from app.models import farm, soil_reading, crop, fertilizer, recommendation  # noqa

    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def seeded_db(db: AsyncSession) -> AsyncSession:
    """DB session with crop references and fertilizer products seeded."""
    from app.services.crop_service import seed_crop_references
    from app.services.fertilizer_service import seed_sample_products
    await seed_crop_references(db)
    await seed_sample_products(db)
    await db.commit()
    return db


@pytest_asyncio.fixture
async def client(seeded_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP test client wired to the FastAPI app with an isolated test database.
    Each test gets a fresh seeded database — changes from one test do not leak.
    """
    async def override_get_db():
        yield seeded_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
