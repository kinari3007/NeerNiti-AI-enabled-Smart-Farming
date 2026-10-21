"""Tests for soil reading submission, validation, and aggregation."""
import pytest
from httpx import AsyncClient

COLLECTED_AT = "2026-10-01T08:00:00+00:00"


async def _make_farm(client: AsyncClient, name: str = "Soil Farm") -> str:
    resp = await client.post("/api/v1/farms", json={"name": name})
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_soil_reading_full(client: AsyncClient):
    farm_id = await _make_farm(client)
    resp = await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "soil_ph": 7.0,
        "electrical_conductivity": 1.2,
        "ec_unit": "dS/m",
        "soil_moisture": 40.0,
        "moisture_unit": "%",
        "nitrogen": 120.0,
        "phosphorus": 60.0,
        "potassium": 200.0,
        "npk_unit": "mg/kg",
        "data_source": "manual",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["soil_ph"] == pytest.approx(7.0)
    assert data["is_validated"] is True
    assert data["validation_flags"] is None


@pytest.mark.asyncio
async def test_soil_reading_all_optional_fields_can_be_absent(client: AsyncClient):
    """A reading with only a timestamp is valid — sensors don't measure everything."""
    farm_id = await _make_farm(client, "MinimalSensorFarm")
    resp = await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "data_source": "sensor",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["soil_ph"] is None
    assert data["nitrogen"] is None


@pytest.mark.asyncio
async def test_soil_reading_ph_out_of_agronomic_range_flagged_not_rejected(client: AsyncClient):
    """pH 3.0 is outside 4.0–8.5 — must be stored with a flag, not rejected."""
    farm_id = await _make_farm(client, "AcidFarm")
    resp = await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "soil_ph": 3.0,
        "data_source": "manual",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_validated"] is False
    assert data["validation_flags"] is not None
    assert "pH" in data["validation_flags"]


@pytest.mark.asyncio
async def test_soil_reading_ph_above_14_rejected(client: AsyncClient):
    """pH > 14 is physically impossible — schema rejects it."""
    farm_id = await _make_farm(client, "ImpossibleFarm")
    resp = await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "soil_ph": 15.0,
        "data_source": "manual",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_soil_reading_high_ec_flagged(client: AsyncClient):
    """EC > 4.0 dS/m should be flagged for salinity."""
    farm_id = await _make_farm(client, "SalineFarm")
    resp = await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "electrical_conductivity": 8.0,
        "ec_unit": "dS/m",
        "data_source": "sensor",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_validated"] is False
    assert "EC" in data["validation_flags"] or "salinity" in data["validation_flags"].lower()


@pytest.mark.asyncio
async def test_soil_reading_npk_without_unit_rejected(client: AsyncClient):
    """NPK value without a unit must be rejected."""
    farm_id = await _make_farm(client, "UnitlessFarm")
    resp = await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "nitrogen": 100.0,
        # npk_unit missing
        "data_source": "manual",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_soil_reading_invalid_data_source_rejected(client: AsyncClient):
    farm_id = await _make_farm(client, "BadSourceFarm")
    resp = await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "data_source": "telescope",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_soil_reading_sampling_coords_must_be_paired(client: AsyncClient):
    farm_id = await _make_farm(client, "HalfCoordFarm")
    resp = await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "sampling_latitude": 28.5,
        # sampling_longitude missing
        "data_source": "manual",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_soil_readings(client: AsyncClient):
    farm_id = await _make_farm(client, "ListFarm")
    for _ in range(3):
        await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
            "collected_at": COLLECTED_AT,
            "soil_ph": 6.5,
            "data_source": "manual",
        })
    resp = await client.get(f"/api/v1/farms/{farm_id}/soil-readings")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


@pytest.mark.asyncio
async def test_soil_summary_stats(client: AsyncClient):
    """Summary should compute mean/median correctly for multiple readings."""
    farm_id = await _make_farm(client, "StatsFarm")
    phs = [6.0, 7.0, 8.0]
    for ph in phs:
        await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
            "collected_at": COLLECTED_AT,
            "soil_ph": ph,
            "data_source": "manual",
        })
    resp = await client.get(f"/api/v1/farms/{farm_id}/soil-summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reading_count"] == 3
    assert data["ph"] is not None
    assert data["ph"]["mean"] == pytest.approx(7.0)
    assert data["ph"]["min"] == pytest.approx(6.0)
    assert data["ph"]["max"] == pytest.approx(8.0)
    assert data["ph"]["count"] == 3


@pytest.mark.asyncio
async def test_soil_summary_mixed_units_excluded(client: AsyncClient):
    """Readings with different NPK units must not be aggregated."""
    farm_id = await _make_farm(client, "MixedUnitFarm")
    await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "nitrogen": 100.0,
        "npk_unit": "mg/kg",
        "data_source": "manual",
    })
    await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "nitrogen": 50.0,
        "npk_unit": "kg/ha",  # different unit
        "data_source": "manual",
    })
    resp = await client.get(f"/api/v1/farms/{farm_id}/soil-summary")
    assert resp.status_code == 200
    data = resp.json()
    # Nitrogen should be None due to mixed units
    assert data["nitrogen"] is None
    assert len(data["unit_notes"]) > 0


@pytest.mark.asyncio
async def test_soil_summary_empty_farm(client: AsyncClient):
    farm_id = await _make_farm(client, "EmptyFarm")
    resp = await client.get(f"/api/v1/farms/{farm_id}/soil-summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["reading_count"] == 0
    assert data["ph"] is None
    assert len(data["warnings"]) > 0


@pytest.mark.asyncio
async def test_soil_reading_unknown_farm(client: AsyncClient):
    resp = await client.post("/api/v1/farms/nonexistent-farm/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "data_source": "manual",
    })
    assert resp.status_code == 404
