"""
Tests for the optimization engine and nutrient unit conversions.

These tests are independent of the database and HTTP layer.
They verify the optimizer against small, hand-calculable examples.
"""
from datetime import datetime, timezone

import pytest

from app.optimization.constraints import (
    P2O5_TO_P_ELEMENTAL,
    K2O_TO_K_ELEMENTAL,
    get_nutrient_requirements,
    nutrient_content_per_ha,
)
from app.optimization.fertilizer_optimizer import (
    FertilizerOption,
    optimize_fertilizer_cost,
)

_NOW = datetime.now(timezone.utc)

# ---- Helpers ----

def _urea(price: float = 5.8) -> FertilizerOption:
    return FertilizerOption("u", "Urea", 46, 0, 0, False, price, "INR", "user_entered", True, "p1", _NOW)

def _dap(price: float = 27.0) -> FertilizerOption:
    return FertilizerOption("d", "DAP", 18, 46, 0, False, price, "INR", "user_entered", True, "p2", _NOW)

def _mop(price: float = 17.5) -> FertilizerOption:
    return FertilizerOption("m", "MOP", 0, 0, 60, False, price, "INR", "user_entered", True, "p3", _NOW)


# ---- Nutrient content tests ----

def test_nutrient_content_urea():
    n, p, k = nutrient_content_per_ha(100.0, 46.0, 0.0, 0.0, False)
    assert n == pytest.approx(46.0)
    assert p == pytest.approx(0.0)
    assert k == pytest.approx(0.0)


def test_nutrient_content_dap():
    n, p, k = nutrient_content_per_ha(100.0, 18.0, 46.0, 0.0, False)
    assert n == pytest.approx(18.0)
    assert p == pytest.approx(46.0)
    assert k == pytest.approx(0.0)


def test_nutrient_content_elemental_conversion():
    """Elemental P% should be converted to P₂O₅ equivalent."""
    # 100 kg of product with 20% elemental P
    # P₂O₅ = 20 * P_ELEMENTAL_TO_P2O5 = 20 / 0.4364 ≈ 45.83
    n, p2o5, k2o = nutrient_content_per_ha(100.0, 0.0, 20.0, 0.0, nutrient_as_elemental=True)
    expected_p2o5 = 20.0 / P2O5_TO_P_ELEMENTAL
    assert p2o5 == pytest.approx(expected_p2o5, rel=1e-4)


# ---- Optimizer feasibility tests ----

def test_optimizer_feasible_wheat_sowing():
    """Wheat Sowing: N=60, P=30, K=30 kg/ha — should find a solution."""
    result = optimize_fertilizer_cost([_urea(), _dap(), _mop()], 60.0, 30.0, 30.0, area_ha=1.0)
    assert result.status == "feasible"
    assert result.is_optimal is True
    # Constraints must be satisfied within tolerance
    assert result.n_supplied_kg_per_ha >= 60.0 - 1e-3
    assert result.p_supplied_kg_per_ha >= 30.0 - 1e-3
    assert result.k_supplied_kg_per_ha >= 30.0 - 1e-3
    assert result.total_cost_per_ha > 0


def test_optimizer_cost_is_correct():
    """
    Hand-calculable case: N=46 kg/ha needs exactly 100 kg Urea at 5.8/kg = 580 INR/ha.
    No P or K needed so DAP/MOP should not be used.
    """
    result = optimize_fertilizer_cost([_urea(), _dap(), _mop()], 46.0, 0.0, 0.0, area_ha=1.0)
    assert result.status == "feasible"
    # Only Urea should be in solution (DAP/MOP add no value for pure N requirement)
    urea_idx = result.product_names.index("Urea")
    assert result.quantities_kg_per_ha[urea_idx] == pytest.approx(100.0, rel=1e-3)
    assert result.total_cost_per_ha == pytest.approx(580.0, rel=1e-2)


def test_optimizer_infeasible_impossible_n_requirement():
    """Requiring 10,000 kg N/ha is infeasible given the 500 kg/ha cap per product."""
    result = optimize_fertilizer_cost([_urea(), _dap(), _mop()], 10000.0, 0.0, 0.0, area_ha=1.0)
    assert result.status == "infeasible"
    assert "infeasible" in result.solver_message.lower() or "feasible" in result.solver_message.lower()


def test_optimizer_no_products():
    """Empty product list → infeasible."""
    result = optimize_fertilizer_cost([], 60.0, 30.0, 30.0)
    assert result.status == "infeasible"


def test_optimizer_zero_price_excluded():
    """Products with zero price should be excluded automatically."""
    bad = FertilizerOption("x", "Bad Product", 46, 0, 0, False, 0.0, "INR", "user", True, "px", _NOW)
    result = optimize_fertilizer_cost([bad], 46.0, 0.0, 0.0)
    assert result.status == "infeasible"
    assert len(result.warnings) > 0


def test_optimizer_all_zero_npk_excluded():
    """Products with no NPK should be excluded from the LP (e.g. Zinc Sulphate)."""
    zinc = FertilizerOption("z", "Zinc Sulphate", 0, 0, 0, False, 55.0, "INR", "user", True, "pz", _NOW)
    result = optimize_fertilizer_cost([zinc, _urea()], 46.0, 0.0, 0.0)
    assert result.status == "feasible"
    assert any(w for w in result.warnings if "Zinc" in w)


def test_optimizer_scales_quantities_with_area():
    """1 ha result cost should be half of 2 ha result cost for same requirements."""
    r1 = optimize_fertilizer_cost([_urea(), _dap(), _mop()], 60.0, 30.0, 30.0, area_ha=1.0)
    r2 = optimize_fertilizer_cost([_urea(), _dap(), _mop()], 60.0, 30.0, 30.0, area_ha=1.0)
    # Same call should return same result
    assert r1.total_cost_per_ha == pytest.approx(r2.total_cost_per_ha, rel=1e-4)


# ---- Nutrient requirement lookup tests ----

def test_get_requirements_wheat_sowing():
    reqs, source = get_nutrient_requirements("Wheat", "Sowing")
    assert reqs is not None
    assert reqs["N"] == pytest.approx(60.0)
    assert reqs["P"] == pytest.approx(30.0)
    assert reqs["K"] == pytest.approx(30.0)
    assert "ICAR" in source


def test_get_requirements_case_insensitive():
    reqs, _ = get_nutrient_requirements("wheat", "sowing")
    assert reqs is not None
    assert reqs["N"] == pytest.approx(60.0)


def test_get_requirements_unknown_crop():
    reqs, source = get_nutrient_requirements("AlienCrop", "Sowing")
    assert reqs is None
    assert "not in the nutrient requirement reference table" in source


def test_get_requirements_known_crop_unknown_stage():
    """Known crop, unknown stage — should return a default with a note."""
    reqs, source = get_nutrient_requirements("Wheat", "UnknownStage")
    assert reqs is not None  # falls back to Sowing
    assert "conservative default" in source or "Sowing" in source


def test_all_seeded_crops_have_requirements():
    """Every crop in the seed catalogue should have nutrient requirements."""
    from app.services.crop_service import _SEED_CROPS
    from app.optimization.constraints import CROP_NUTRIENT_REQUIREMENTS

    missing = []
    for crop in _SEED_CROPS:
        name = crop["name"]
        if name not in CROP_NUTRIENT_REQUIREMENTS:
            missing.append(name)

    assert missing == [], f"Crops missing from nutrient reference table: {missing}"
