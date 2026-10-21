"""Tests for the /health endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_db_returns_connected(client: AsyncClient):
    response = await client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "connected"
    assert data["status"] == "ok"
