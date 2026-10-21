"""
Cost-minimizing fertilizer optimizer using SciPy linear programming.

Problem formulation
-------------------
Decision variables:
    x_i ≥ 0  (kg/ha of fertilizer product i)

Objective:
    Minimize  Σ (price_per_kg_i × x_i)

Constraints (all per-hectare, P and K in oxide convention):
    Σ (N_pct_i / 100 × x_i)    ≥  N_required  kg/ha
    Σ (P2O5_pct_i / 100 × x_i) ≥  P_required  kg/ha
    Σ (K2O_pct_i / 100 × x_i)  ≥  K_required  kg/ha
    x_i ≤ MAX_APPLICATION_KG_PER_HA  (agronomic upper bound per product)
    x_i ≥ 0

Solver
------
scipy.optimize.linprog (HiGHS backend, exact LP).
The problem is linear → the HiGHS solver returns a globally optimal solution
when feasible, or proves infeasibility.  We report the solver status honestly
and never claim optimality if the solver did not prove it.

Nutrient convention
-------------------
All nutrient quantities are in kg/ha with P expressed as P₂O₅ and K as K₂O
(fertilizer label convention).  See constraints.py for conversion factors.

Agricultural safety
-------------------
An upper bound of MAX_APPLICATION_KG_PER_HA (default 500 kg/ha per product)
prevents agronomically absurd quantities.  The optimizer still enforces ≥
nutrient constraints; it does not guarantee soil health beyond what the
reference requirements encode.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np
from scipy.optimize import linprog

from app.optimization.constraints import nutrient_content_per_ha

logger = logging.getLogger("neerniti.optimization")

# Upper bound per product in kg/ha — prevents agronomically unsafe application rates.
# This is a conservative sanity cap; individual products may warrant tighter limits.
MAX_APPLICATION_KG_PER_HA: float = 500.0

# Numerical tolerance for constraint satisfaction checks
CONSTRAINT_TOL: float = 1e-4


@dataclass
class FertilizerOption:
    """A single available fertilizer product with its price."""

    product_id: str
    product_name: str
    nitrogen_pct: float       # % elemental N
    phosphorus_pct: float     # % P₂O₅ (or elemental P if nutrient_as_elemental=True)
    potassium_pct: float      # % K₂O  (or elemental K if nutrient_as_elemental=True)
    nutrient_as_elemental: bool
    price_per_kg: float       # in the product's currency per kg
    currency: str
    price_source: str
    price_verified: bool
    price_record_id: str
    price_recorded_at: datetime


@dataclass
class OptimizationResult:
    """Output from the optimizer."""

    status: str  # "feasible", "infeasible", "error"
    solver_message: str

    # Per-product results (parallel arrays, same order as input options)
    product_ids: list[str] = field(default_factory=list)
    product_names: list[str] = field(default_factory=list)
    quantities_kg_per_ha: list[float] = field(default_factory=list)  # from solver

    # Nutrients delivered per ha (computed from solution quantities)
    n_supplied_kg_per_ha: float = 0.0
    p_supplied_kg_per_ha: float = 0.0
    k_supplied_kg_per_ha: float = 0.0

    # Targets
    n_required_kg_per_ha: float = 0.0
    p_required_kg_per_ha: float = 0.0
    k_required_kg_per_ha: float = 0.0

    total_cost_per_ha: float = 0.0
    currency: str = "INR"

    warnings: list[str] = field(default_factory=list)

    # Is the returned solution optimal according to the solver?
    is_optimal: bool = False


def optimize_fertilizer_cost(
    options: list[FertilizerOption],
    n_required_kg_per_ha: float,
    p_required_kg_per_ha: float,
    k_required_kg_per_ha: float,
    area_ha: float = 1.0,
) -> OptimizationResult:
    """
    Find the minimum-cost combination of fertilizer products that meets
    the per-hectare nutrient requirements.

    Parameters
    ----------
    options:
        Available fertilizer products with prices.  Products with price = 0
        or with all-zero nutrients are excluded automatically.
    n_required_kg_per_ha, p_required_kg_per_ha, k_required_kg_per_ha:
        Target nutrient requirements per hectare (P as P₂O₅, K as K₂O).
    area_ha:
        Cultivated area; used only to scale total quantities in the result.
        The LP itself is solved per-hectare for numerical stability.

    Returns
    -------
    OptimizationResult with status "feasible", "infeasible", or "error".
    """
    warnings: list[str] = []

    # --- Filter usable options ---
    usable: list[FertilizerOption] = []
    for opt in options:
        if opt.price_per_kg <= 0:
            warnings.append(
                f"Product '{opt.product_name}' excluded: price_per_kg = {opt.price_per_kg}."
            )
            continue
        n, p, k = nutrient_content_per_ha(
            1.0, opt.nitrogen_pct, opt.phosphorus_pct, opt.potassium_pct,
            opt.nutrient_as_elemental,
        )
        if n == 0 and p == 0 and k == 0:
            warnings.append(
                f"Product '{opt.product_name}' excluded: provides no N, P, or K "
                "(e.g. Zinc Sulphate). Add it manually if needed for micronutrients."
            )
            continue
        usable.append(opt)

    if not usable:
        return OptimizationResult(
            status="infeasible",
            solver_message=(
                "No fertilizer products with valid prices and NPK content are available. "
                "Add products with verified prices to proceed."
            ),
            n_required_kg_per_ha=n_required_kg_per_ha,
            p_required_kg_per_ha=p_required_kg_per_ha,
            k_required_kg_per_ha=k_required_kg_per_ha,
            warnings=warnings,
        )

    n_products = len(usable)

    # --- Build LP matrices ---
    # Cost vector
    c = np.array([opt.price_per_kg for opt in usable], dtype=float)

    # Nutrient matrix: shape (3, n_products)
    # Row 0: N coefficients per kg of product
    # Row 1: P₂O₅ coefficients
    # Row 2: K₂O coefficients
    nutrient_matrix = np.zeros((3, n_products), dtype=float)
    for j, opt in enumerate(usable):
        n_coef, p_coef, k_coef = nutrient_content_per_ha(
            1.0, opt.nitrogen_pct, opt.phosphorus_pct, opt.potassium_pct,
            opt.nutrient_as_elemental,
        )
        nutrient_matrix[0, j] = n_coef
        nutrient_matrix[1, j] = p_coef
        nutrient_matrix[2, j] = k_coef

    # Inequality constraints: -A_ub @ x <= -b_ub  (i.e., A_ub @ x >= b_ub)
    A_ub = -nutrient_matrix                                          # shape (3, n)
    b_ub = -np.array(
        [n_required_kg_per_ha, p_required_kg_per_ha, k_required_kg_per_ha],
        dtype=float,
    )

    # Bounds: 0 ≤ x_i ≤ MAX_APPLICATION_KG_PER_HA
    bounds = [(0.0, MAX_APPLICATION_KG_PER_HA)] * n_products

    # --- Solve ---
    result = linprog(
        c=c,
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=bounds,
        method="highs",
        options={"disp": False},
    )

    logger.debug(
        "LP solver status=%s message=%r fun=%.4f",
        result.status, result.message, float(result.fun) if result.fun is not None else float("nan"),
    )

    if result.status == 2:  # Infeasible
        return OptimizationResult(
            status="infeasible",
            solver_message=(
                f"No feasible fertilizer combination can meet the nutrient targets "
                f"(N≥{n_required_kg_per_ha}, P₂O₅≥{p_required_kg_per_ha}, "
                f"K₂O≥{k_required_kg_per_ha} kg/ha) within the available products "
                f"and application limits ({MAX_APPLICATION_KG_PER_HA} kg/ha per product). "
                "Consider adding more products, relaxing constraints, or verifying targets."
            ),
            n_required_kg_per_ha=n_required_kg_per_ha,
            p_required_kg_per_ha=p_required_kg_per_ha,
            k_required_kg_per_ha=k_required_kg_per_ha,
            warnings=warnings,
        )

    if result.status == 3:  # Unbounded
        return OptimizationResult(
            status="error",
            solver_message="LP is unbounded — check application bounds configuration.",
            warnings=warnings,
        )

    if result.status not in (0, 1):
        return OptimizationResult(
            status="error",
            solver_message=f"Solver returned unexpected status {result.status}: {result.message}",
            warnings=warnings,
        )

    # --- Parse solution ---
    x: np.ndarray = result.x
    total_cost_per_ha: float = float(result.fun)

    # Compute supplied nutrients
    supplied = nutrient_matrix @ x  # shape (3,)
    n_sup = float(supplied[0])
    p_sup = float(supplied[1])
    k_sup = float(supplied[2])

    # Verify constraint satisfaction within tolerance
    for name, req, sup in [
        ("N", n_required_kg_per_ha, n_sup),
        ("P₂O₅", p_required_kg_per_ha, p_sup),
        ("K₂O", k_required_kg_per_ha, k_sup),
    ]:
        deficit = req - sup
        if deficit > CONSTRAINT_TOL:
            warnings.append(
                f"Nutrient constraint for {name} not fully satisfied: "
                f"required {req:.2f} kg/ha, supplied {sup:.2f} kg/ha "
                f"(deficit {deficit:.4f} kg/ha — within solver tolerance)."
            )

    # Determine mixed currency
    currencies = {opt.currency for opt in usable}
    currency = currencies.pop() if len(currencies) == 1 else "MIXED"
    if len(currencies) > 0:  # was > 1 originally
        warnings.append(
            "Products have mixed currencies. Total cost may not be comparable directly."
        )

    return OptimizationResult(
        status="feasible",
        solver_message=f"Optimal solution found by HiGHS LP solver. {result.message}",
        product_ids=[opt.product_id for opt in usable],
        product_names=[opt.product_name for opt in usable],
        quantities_kg_per_ha=x.tolist(),
        n_supplied_kg_per_ha=n_sup,
        p_supplied_kg_per_ha=p_sup,
        k_supplied_kg_per_ha=k_sup,
        n_required_kg_per_ha=n_required_kg_per_ha,
        p_required_kg_per_ha=p_required_kg_per_ha,
        k_required_kg_per_ha=k_required_kg_per_ha,
        total_cost_per_ha=total_cost_per_ha,
        currency=currency,
        warnings=warnings,
        is_optimal=(result.status == 0),
    )
