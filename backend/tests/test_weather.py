"""
Tests for the weather service.
All tests mock the external HTTP call — no live network access required.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


async def _make_farm_with_coords(client: AsyncClient) -> str:
    resp = await client.post("/api/v1/farms", json={
        "name": "Weather Farm",
        "latitude": 28.6139,
        "longitude": 77.2090,
    })
    return resp.json()["id"]


async def _make_farm_no_coords(client: AsyncClient) -> str:
    resp = await client.post("/api/v1/farms", json={"name": "No Coords Farm"})
    return resp.json()["id"]


def _mock_open_meteo_response() -> dict:
    return {
        "current": {
            "time": "2026-10-21T09:00",
            "temperature_2m": 28.5,
            "relative_humidity_2m": 65.0,
            "precipitation": 0.0,
            "wind_speed_10m": 12.0,
            "weather_code": 1,
        },
        "daily": {
            "time": ["2026-10-21", "2026-10-22"],
            "temperature_2m_max": [31.0, 30.5],
            "temperature_2m_min": [18.0, 17.5],
            "precipitation_sum": [0.0, 2.5],
            "precipitation_probability_max": [5, 40],
        },
    }


@pytest.mark.asyncio
async def test_weather_requires_farm_coordinates(client: AsyncClient):
    farm_id = await _make_farm_no_coords(client)
    resp = await client.get(f"/api/v1/farms/{farm_id}/weather")
    assert resp.status_code == 422
    assert "coordinates" in resp.json()["message"].lower()


@pytest.mark.asyncio
async def test_weather_farm_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/farms/nonexistent-farm/weather")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_weather_success_mocked(client: AsyncClient):
    """Mock Open-Meteo response and verify schema parsing."""
    from app.services import weather_service
    weather_service.clear_weather_cache()

    farm_id = await _make_farm_with_coords(client)

    mock_resp = MagicMock()
    mock_resp.json.return_value = _mock_open_meteo_response()
    mock_resp.raise_for_status = MagicMock()

    with patch("app.services.weather_service.httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        resp = await client.get(f"/api/v1/farms/{farm_id}/weather")

    assert resp.status_code == 200
    data = resp.json()
    assert data["farm_id"] == farm_id
    assert data["current"]["temperature_2m"] == pytest.approx(28.5)
    assert data["current"]["relative_humidity_2m"] == pytest.approx(65.0)
    assert len(data["forecast_days"]) == 2
    assert data["is_cached"] is False
    assert "Open-Meteo" in data["data_source"]


@pytest.mark.asyncio
async def test_weather_cached_on_second_call(client: AsyncClient):
    """Second call for same coordinates should be served from cache."""
    from app.services import weather_service
    weather_service.clear_weather_cache()

    farm_id = await _make_farm_with_coords(client)

    mock_resp = MagicMock()
    mock_resp.json.return_value = _mock_open_meteo_response()
    mock_resp.raise_for_status = MagicMock()

    with patch("app.services.weather_service.httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        await client.get(f"/api/v1/farms/{farm_id}/weather")  # first call
        resp2 = await client.get(f"/api/v1/farms/{farm_id}/weather")  # second

    data = resp2.json()
    assert data["is_cached"] is True
    # HTTP client should have been called only once
    assert mock_http.get.call_count == 1


@pytest.mark.asyncio
async def test_weather_api_timeout_handled(client: AsyncClient):
    """Timeout should return 422 with a clear message, not 500."""
    from app.services import weather_service
    import httpx
    weather_service.clear_weather_cache()

    farm_id = await _make_farm_with_coords(client)

    with patch("app.services.weather_service.httpx.AsyncClient") as mock_client_cls:
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_http)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        resp = await client.get(f"/api/v1/farms/{farm_id}/weather")

    assert resp.status_code == 422
    assert "timed out" in resp.json()["message"].lower() or "unavailable" in resp.json()["message"].lower()
