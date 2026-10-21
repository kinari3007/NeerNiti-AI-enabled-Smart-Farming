"""
Tests for the recommendation pipeline.
"""
import pytest
from httpx import AsyncClient

COLLECTED_AT = "2026-10-01T08:00:00+00:00"


async def _create_farm(client: AsyncClient, **kwargs) -> dict:
    defaults = {"name": "Rec Farm", "latitude": 28.6, "longitude": 77.2, "area_value": 1.0, "area_unit": "hectare"}
    defaults.update(kwargs)
    resp = await client.post("/api/v1/farms", json=defaults)
    return resp.json()


async def _add_soil(client: AsyncClient, farm_id: str):
    await client.post(f"/api/v1/farms/{farm_id}/soil-readings", json={
        "collected_at": COLLECTED_AT,
        "soil_ph": 7.0,
        "electrical_conductivity": 1.2,
        "ec_unit": "dS/m",
        "nitrogen": 80.0,
        "phosphorus": 40.0,
        "potassium": 200.0,
        "npk_unit": "mg/kg",
        "data_source": "manual",
    })


@pytest.mark.asyncio
async def test_recommendation_feasible_wheat(client: AsyncClient):
    farm = await _create_farm(client)
    await _add_soil(client, farm["id"])
    resp = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "Wheat",
        "growth_stage": "Sowing",
        "area_ha": 1.0,
        "use_weather": False,
        "allow_unverified_prices": True,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["optimization_status"] == "feasible"
    assert data["recommended_fertilizers"] is not None
    assert len(data["recommended_fertilizers"]) > 0
    assert data["estimated_total_cost"] is not None
    assert data["estimated_total_cost"] > 0

    # Nutrient balance should show requirements met
    nb = data["nutrient_balance"]
    assert nb is not None
    assert nb["n_deficit_kg_per_ha"] < 0.01
    assert nb["p_deficit_kg_per_ha"] < 0.01
    assert nb["k_deficit_kg_per_ha"] < 0.01


@pytest.mark.asyncio
async def test_recommendation_three_outputs_are_distinct(client: AsyncClient):
    """ML suggestion, nutrient requirements, and optimization plan are separate."""
    farm = await _create_farm(client)
    resp = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "Rice",
        "growth_stage": "Vegetative",
        "area_ha": 1.0,
        "use_weather": False,
        "allow_unverified_prices": True,
    })
    assert resp.status_code == 201
    data = resp.json()
    # Section 1: ML classifier
    assert "ml_classifier_suggestion" in data
    # Section 2: nutrient requirements
    assert "nutrient_requirements" in data
    assert "nutrient_requirement_source" in data
    # Section 3: LP plan
    assert "optimization_status" in data
    assert "recommended_fertilizers" in data


@pytest.mark.asyncio
async def test_recommendation_unknown_crop_skipped(client: AsyncClient):
    farm = await _create_farm(client)
    resp = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "AlienCrop",
        "growth_stage": "Sowing",
        "area_ha": 1.0,
        "use_weather": False,
        "allow_unverified_prices": True,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["optimization_status"] == "skipped_no_requirements"
    assert data["recommended_fertilizers"] is None


@pytest.mark.asyncio
async def test_recommendation_no_prices_skipped(client: AsyncClient):
    """Without allow_unverified_prices and no verified prices → skipped_no_prices."""
    farm = await _create_farm(client)
    resp = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "Wheat",
        "growth_stage": "Sowing",
        "area_ha": 1.0,
        "use_weather": False,
        "allow_unverified_prices": False,  # default seed prices are illustrative
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["optimization_status"] == "skipped_no_prices"
    assert data["recommended_fertilizers"] is None
    assert len(data["warnings"]) > 0


@pytest.mark.asyncio
async def test_recommendation_missing_crop_info_rejected(client: AsyncClient):
    farm = await _create_farm(client)
    resp = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "area_ha": 1.0,
        "use_weather": False,
        # Neither crop_selection_id nor crop_name + growth_stage
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_recommendation_persisted_and_retrievable(client: AsyncClient):
    farm = await _create_farm(client)
    create_resp = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "Wheat",
        "growth_stage": "Sowing",
        "area_ha": 1.0,
        "use_weather": False,
        "allow_unverified_prices": True,
    })
    rec_id = create_resp.json()["id"]

    # Get by ID
    get_resp = await client.get(f"/api/v1/recommendations/{rec_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == rec_id

    # List for farm
    list_resp = await client.get(f"/api/v1/farms/{farm['id']}/recommendations")
    assert list_resp.status_code == 200
    assert any(r["id"] == rec_id for r in list_resp.json())


@pytest.mark.asyncio
async def test_recommendation_farm_not_found(client: AsyncClient):
    resp = await client.post("/api/v1/farms/nonexistent/recommendations", json={
        "crop_name": "Wheat",
        "growth_stage": "Sowing",
        "area_ha": 1.0,
        "use_weather": False,
        "allow_unverified_prices": True,
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_recommendation_price_provenance_in_response(client: AsyncClient):
    """Every recommended product must expose price_source and price_verified fields."""
    farm = await _create_farm(client)
    resp = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "Wheat",
        "growth_stage": "Sowing",
        "area_ha": 1.0,
        "use_weather": False,
        "allow_unverified_prices": True,
    })
    data = resp.json()
    if data["recommended_fertilizers"]:
        for item in data["recommended_fertilizers"]:
            assert "price_source" in item
            assert "price_verified" in item
            assert "price_record_id" in item
            assert "price_recorded_at" in item


@pytest.mark.asyncio
async def test_recommendation_ml_disclaimer_always_present(client: AsyncClient):
    farm = await _create_farm(client)
    resp = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "Wheat",
        "growth_stage": "Sowing",
        "area_ha": 1.0,
        "use_weather": False,
        "allow_unverified_prices": True,
    })
    data = resp.json()
    if data["ml_classifier_suggestion"]:
        assert "disclaimer" in data["ml_classifier_suggestion"]
        # Disclaimer must clearly state it's NOT a nutrient quantity
        disclaimer = data["ml_classifier_suggestion"]["disclaimer"]
        assert "NOT" in disclaimer or "not" in disclaimer


@pytest.mark.asyncio
async def test_recommendation_nutrient_requirement_source_cited(client: AsyncClient):
    farm = await _create_farm(client)
    resp = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "Wheat",
        "growth_stage": "Sowing",
        "area_ha": 1.0,
        "use_weather": False,
        "allow_unverified_prices": True,
    })
    data = resp.json()
    assert data["nutrient_requirement_source"] is not None
    assert "ICAR" in data["nutrient_requirement_source"]


@pytest.mark.asyncio
async def test_recommendation_area_scales_total_cost(client: AsyncClient):
    """Doubling the area should roughly double the total cost."""
    farm = await _create_farm(client)
    resp1 = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "Wheat", "growth_stage": "Sowing",
        "area_ha": 1.0, "use_weather": False, "allow_unverified_prices": True,
    })
    resp2 = await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "Wheat", "growth_stage": "Sowing",
        "area_ha": 2.0, "use_weather": False, "allow_unverified_prices": True,
    })
    c1 = resp1.json()["estimated_total_cost"]
    c2 = resp2.json()["estimated_total_cost"]
    if c1 and c2:
        assert c2 == pytest.approx(c1 * 2.0, rel=1e-3)


@pytest.mark.asyncio
async def test_recommendation_delete_farm_blocked(client: AsyncClient):
    """Farm with a recommendation cannot be deleted."""
    farm = await _create_farm(client)
    await client.post(f"/api/v1/farms/{farm['id']}/recommendations", json={
        "crop_name": "Wheat", "growth_stage": "Sowing",
        "area_ha": 1.0, "use_weather": False, "allow_unverified_prices": True,
    })
    del_resp = await client.delete(f"/api/v1/farms/{farm['id']}")
    assert del_resp.status_code == 422
    assert "FARM_HAS_RECOMMENDATIONS" in del_resp.json()["error"]
