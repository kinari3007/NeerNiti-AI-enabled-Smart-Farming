"""Tests for Farm CRUD endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_farm_minimal(client: AsyncClient):
    resp = await client.post("/api/v1/farms", json={"name": "Test Farm"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Farm"
    assert data["id"]
    assert data["latitude"] is None
    assert data["longitude"] is None


@pytest.mark.asyncio
async def test_create_farm_with_coordinates(client: AsyncClient):
    resp = await client.post("/api/v1/farms", json={
        "name": "Geo Farm",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "area_value": 5.0,
        "area_unit": "hectare",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["latitude"] == pytest.approx(28.6139)
    assert data["longitude"] == pytest.approx(77.2090)
    assert data["area_unit"] == "hectare"


@pytest.mark.asyncio
async def test_create_farm_coordinates_must_be_paired(client: AsyncClient):
    """Latitude without longitude must be rejected."""
    resp = await client.post("/api/v1/farms", json={
        "name": "Bad Farm",
        "latitude": 28.6,
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_farm_invalid_area_unit(client: AsyncClient):
    resp = await client.post("/api/v1/farms", json={
        "name": "Bad Unit Farm",
        "area_value": 1.0,
        "area_unit": "furlongs",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_farm(client: AsyncClient):
    create = await client.post("/api/v1/farms", json={"name": "Retrieve Me"})
    farm_id = create.json()["id"]
    resp = await client.get(f"/api/v1/farms/{farm_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == farm_id


@pytest.mark.asyncio
async def test_get_farm_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/farms/nonexistent-id-0000")
    assert resp.status_code == 404
    assert resp.json()["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_list_farms_pagination(client: AsyncClient):
    # Create 3 farms
    for i in range(3):
        await client.post("/api/v1/farms", json={"name": f"Farm {i}"})
    resp = await client.get("/api/v1/farms?page=1&page_size=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 2


@pytest.mark.asyncio
async def test_update_farm(client: AsyncClient):
    create = await client.post("/api/v1/farms", json={"name": "Old Name"})
    farm_id = create.json()["id"]
    resp = await client.patch(f"/api/v1/farms/{farm_id}", json={"name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_delete_farm_no_recommendations(client: AsyncClient):
    create = await client.post("/api/v1/farms", json={"name": "Delete Me"})
    farm_id = create.json()["id"]
    resp = await client.delete(f"/api/v1/farms/{farm_id}")
    assert resp.status_code == 200
    # Confirm gone
    get_resp = await client.get(f"/api/v1/farms/{farm_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_farm_with_irrigation_ph(client: AsyncClient):
    resp = await client.post("/api/v1/farms", json={
        "name": "Irrigated Farm",
        "latitude": 25.0,
        "longitude": 80.0,
        "irrigation_water_ph": 7.5,
        "irrigation_water_ph_source": "pH meter",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["irrigation_water_ph"] == pytest.approx(7.5)
    assert data["irrigation_water_ph_timestamp"] is not None


@pytest.mark.asyncio
async def test_farm_invalid_irrigation_ph(client: AsyncClient):
    resp = await client.post("/api/v1/farms", json={
        "name": "Bad pH Farm",
        "irrigation_water_ph": 15.0,  # > 14, invalid
    })
    assert resp.status_code == 422
