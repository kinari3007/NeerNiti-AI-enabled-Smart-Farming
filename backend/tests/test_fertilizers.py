"""Tests for fertilizer product and price management."""
import pytest
from httpx import AsyncClient

ADMIN_KEY = "change-me-in-production"  # matches default in config.py


@pytest.mark.asyncio
async def test_list_fertilizers_seeded(client: AsyncClient):
    resp = await client.get("/api/v1/fertilizers")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 8
    names = {f["name"] for f in data["items"]}
    assert "Urea" in names
    assert "DAP (Di-ammonium Phosphate)" in names
    assert "MOP (Muriate of Potash)" in names


@pytest.mark.asyncio
async def test_get_fertilizer_by_id(client: AsyncClient):
    list_resp = await client.get("/api/v1/fertilizers")
    fert = list_resp.json()["items"][0]
    resp = await client.get(f"/api/v1/fertilizers/{fert['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == fert["id"]


@pytest.mark.asyncio
async def test_get_fertilizer_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/fertilizers/no-such-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_prices_returns_illustrative_samples(client: AsyncClient):
    resp = await client.get("/api/v1/fertilizers/prices")
    assert resp.status_code == 200
    prices = resp.json()
    assert len(prices) >= 7  # seeds create at least 7 prices
    sources = {p["source"] for p in prices}
    assert "illustrative_sample" in sources
    # All illustrative samples must be unverified
    for p in prices:
        if p["source"] == "illustrative_sample":
            assert p["is_verified"] is False


@pytest.mark.asyncio
async def test_create_fertilizer_requires_admin_key(client: AsyncClient):
    resp = await client.post("/api/v1/fertilizers", json={
        "name": "Test NPK",
        "nitrogen_pct": 10.0,
        "phosphorus_pct": 10.0,
        "potassium_pct": 10.0,
    })
    assert resp.status_code == 422  # missing header → validation error


@pytest.mark.asyncio
async def test_create_fertilizer_wrong_key(client: AsyncClient):
    resp = await client.post("/api/v1/fertilizers",
        headers={"X-API-Key": "wrong-key"},
        json={"name": "Test NPK", "nitrogen_pct": 10.0},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_fertilizer_with_admin_key(client: AsyncClient):
    resp = await client.post("/api/v1/fertilizers",
        headers={"X-API-Key": ADMIN_KEY},
        json={
            "name": "Custom NPK 20-20-20",
            "nitrogen_pct": 20.0,
            "phosphorus_pct": 20.0,
            "potassium_pct": 20.0,
            "nutrient_basis_note": "20% each of N, P₂O₅, K₂O",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Custom NPK 20-20-20"
    assert data["nitrogen_pct"] == pytest.approx(20.0)


@pytest.mark.asyncio
async def test_create_fertilizer_nutrient_sum_exceeds_100_rejected(client: AsyncClient):
    resp = await client.post("/api/v1/fertilizers",
        headers={"X-API-Key": ADMIN_KEY},
        json={
            "name": "Bad Product",
            "nitrogen_pct": 50.0,
            "phosphorus_pct": 50.0,
            "potassium_pct": 50.0,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_import_prices_csv(client: AsyncClient):
    csv_content = (
        "product_name,price_value,currency,price_unit,supplier,location,source,is_verified,bag_weight_kg\n"
        "Urea,6.50,INR,INR/kg,State Cooperative,Agra UP,verified_market,true,\n"
        "DAP (Di-ammonium Phosphate),28.00,INR,INR/bag,IFFCO,Delhi,csv_import,false,50\n"
        "NonExistentProduct,99.00,INR,INR/kg,,,csv_import,false,\n"  # should be skipped
    )
    resp = await client.post(
        "/api/v1/fertilizers/prices/import",
        headers={"X-API-Key": ADMIN_KEY},
        files={"file": ("prices.csv", csv_content.encode(), "text/csv")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == 2
    assert data["skipped"] == 1
    assert len(data["errors"]) >= 1  # NonExistentProduct error recorded

    # Verify the Urea verified price now appears
    prices_resp = await client.get("/api/v1/fertilizers/prices?verified_only=true")
    prices = prices_resp.json()
    urea_prices = [p for p in prices if p["source"] == "verified_market"]
    assert any(abs(p["price_value"] - 6.5) < 0.01 for p in urea_prices)


@pytest.mark.asyncio
async def test_import_prices_requires_admin_key(client: AsyncClient):
    csv_content = b"product_name,price_value,currency,price_unit\nUrea,5.0,INR,INR/kg\n"
    resp = await client.post(
        "/api/v1/fertilizers/prices/import",
        files={"file": ("p.csv", csv_content, "text/csv")},
    )
    assert resp.status_code == 422  # missing header


@pytest.mark.asyncio
async def test_import_prices_non_csv_rejected(client: AsyncClient):
    resp = await client.post(
        "/api/v1/fertilizers/prices/import",
        headers={"X-API-Key": ADMIN_KEY},
        files={"file": ("data.xlsx", b"fake bytes", "application/octet-stream")},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_nutrient_unit_convention_documented(client: AsyncClient):
    """Ensure the nutrient_basis_note is present for seed products so convention is clear."""
    resp = await client.get("/api/v1/fertilizers")
    items = resp.json()["items"]
    dap = next((f for f in items if "DAP" in f["name"]), None)
    assert dap is not None
    assert dap["nutrient_basis_note"] is not None
    assert "P₂O₅" in dap["nutrient_basis_note"] or "P2O5" in dap["nutrient_basis_note"]
