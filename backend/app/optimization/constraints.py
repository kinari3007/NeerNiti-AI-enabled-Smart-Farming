"""
Nutrient unit conversions and agronomic reference data.

Nutrient Accounting Convention
-------------------------------
All nutrient quantities in this codebase are expressed in the **oxide convention**
used on Indian fertilizer labels, unless noted otherwise:

  N  → elemental nitrogen (kg/ha)  — same in both conventions
  P  → as P₂O₅ (kg/ha)            — NOT elemental P
  K  → as K₂O  (kg/ha)            — NOT elemental K

Fertilizer product composition is stored in the same convention
(phosphorus_pct = % P₂O₅, potassium_pct = % K₂O) unless the product's
nutrient_as_elemental flag is True.

Crop nutrient requirements below are also expressed in this convention
so that they can be directly compared against fertilizer label values
without any further conversion.

Conversion factors (provided for reference):
  P_elemental  = P₂O₅ × 0.4364   (multiply to convert P₂O₅ → elemental P)
  K_elemental  = K₂O  × 0.8301   (multiply to convert K₂O  → elemental K)
  P₂O₅        = P_elemental × 2.2913
  K₂O         = K_elemental × 1.2046

Crop Nutrient Requirements Source
----------------------------------
Values are approximate general guidelines derived from Indian Council of
Agricultural Research (ICAR) crop production recommendations. They represent
total seasonal requirements as commonly cited in extension literature.

THESE ARE NOT FIELD-CALIBRATED REQUIREMENTS. Actual requirements vary with:
  - Soil test values (available nutrients already in soil)
  - Crop variety and expected yield
  - Irrigation regime and rainfall
  - Soil type and organic matter content
  - Local agronomic conditions

Always consult a certified agronomist or ICAR regional extension for
field-specific fertilizer recommendations.
"""

# ---------------------------------------------------------------------------
# Conversion constants
# ---------------------------------------------------------------------------

P2O5_TO_P_ELEMENTAL: float = 0.4364
K2O_TO_K_ELEMENTAL: float = 0.8301
P_ELEMENTAL_TO_P2O5: float = 1.0 / P2O5_TO_P_ELEMENTAL   # ≈ 2.2913
K_ELEMENTAL_TO_K2O: float = 1.0 / K2O_TO_K_ELEMENTAL      # ≈ 1.2046


def nutrient_content_per_ha(
    quantity_kg_per_ha: float,
    nitrogen_pct: float,
    phosphorus_pct: float,
    potassium_pct: float,
    nutrient_as_elemental: bool = False,
) -> tuple[float, float, float]:
    """
    Compute nutrients delivered by a given quantity of fertilizer (per hectare).

    Returns (N_kg_per_ha, P2O5_kg_per_ha, K2O_kg_per_ha).

    If nutrient_as_elemental=True, the product stores elemental P% and K%;
    this function converts them to the P₂O₅/K₂O convention before returning
    so all downstream comparisons remain consistent.
    """
    n_kg = quantity_kg_per_ha * nitrogen_pct / 100.0

    if nutrient_as_elemental:
        p2o5_kg = quantity_kg_per_ha * phosphorus_pct / 100.0 * P_ELEMENTAL_TO_P2O5
        k2o_kg = quantity_kg_per_ha * potassium_pct / 100.0 * K_ELEMENTAL_TO_K2O
    else:
        p2o5_kg = quantity_kg_per_ha * phosphorus_pct / 100.0
        k2o_kg = quantity_kg_per_ha * potassium_pct / 100.0

    return n_kg, p2o5_kg, k2o_kg


# ---------------------------------------------------------------------------
# Crop nutrient requirement reference table
# ---------------------------------------------------------------------------
# Structure: crop_name → growth_stage → {N, P, K} in kg/ha (P as P₂O₅, K as K₂O)
# These are the *total seasonal* application targets cited in ICAR guidelines.
# Source: approximate values from ICAR crop production recommendations (general).

CROP_NUTRIENT_REQUIREMENTS: dict[str, dict[str, dict[str, float]]] = {
    "Wheat": {
        "Sowing":     {"N": 60.0,  "P": 30.0,  "K": 30.0},
        "Germination":{"N": 60.0,  "P": 30.0,  "K": 30.0},
        "Vegetative": {"N": 80.0,  "P": 40.0,  "K": 40.0},
        "Flowering":  {"N": 120.0, "P": 60.0,  "K": 40.0},
        "Maturity":   {"N": 120.0, "P": 60.0,  "K": 40.0},
        "Harvest":    {"N": 120.0, "P": 60.0,  "K": 40.0},
    },
    "Rice": {
        "Sowing":     {"N": 40.0,  "P": 20.0,  "K": 20.0},
        "Germination":{"N": 40.0,  "P": 20.0,  "K": 20.0},
        "Vegetative": {"N": 80.0,  "P": 40.0,  "K": 40.0},
        "Flowering":  {"N": 100.0, "P": 50.0,  "K": 50.0},
        "Maturity":   {"N": 100.0, "P": 50.0,  "K": 50.0},
        "Harvest":    {"N": 100.0, "P": 50.0,  "K": 50.0},
    },
    "Maize": {
        "Sowing":     {"N": 50.0,  "P": 25.0,  "K": 25.0},
        "Germination":{"N": 50.0,  "P": 25.0,  "K": 25.0},
        "Vegetative": {"N": 100.0, "P": 50.0,  "K": 50.0},
        "Flowering":  {"N": 120.0, "P": 60.0,  "K": 40.0},
        "Maturity":   {"N": 120.0, "P": 60.0,  "K": 40.0},
        "Harvest":    {"N": 120.0, "P": 60.0,  "K": 40.0},
    },
    "Cotton": {
        "Sowing":     {"N": 30.0,  "P": 15.0,  "K": 15.0},
        "Germination":{"N": 30.0,  "P": 15.0,  "K": 15.0},
        "Vegetative": {"N": 80.0,  "P": 40.0,  "K": 40.0},
        "Flowering":  {"N": 100.0, "P": 50.0,  "K": 50.0},
        "Maturity":   {"N": 100.0, "P": 50.0,  "K": 50.0},
        "Harvest":    {"N": 100.0, "P": 50.0,  "K": 50.0},
    },
    "Potato": {
        "Sowing":     {"N": 60.0,  "P": 100.0, "K": 100.0},
        "Germination":{"N": 60.0,  "P": 100.0, "K": 100.0},
        "Vegetative": {"N": 120.0, "P": 100.0, "K": 100.0},
        "Flowering":  {"N": 150.0, "P": 100.0, "K": 120.0},
        "Maturity":   {"N": 150.0, "P": 100.0, "K": 120.0},
        "Harvest":    {"N": 150.0, "P": 100.0, "K": 120.0},
    },
    "Sugarcane": {
        "Sowing":     {"N": 50.0,  "P": 50.0,  "K": 50.0},
        "Germination":{"N": 50.0,  "P": 50.0,  "K": 50.0},
        "Vegetative": {"N": 150.0, "P": 50.0,  "K": 100.0},
        "Flowering":  {"N": 200.0, "P": 60.0,  "K": 120.0},
        "Maturity":   {"N": 200.0, "P": 60.0,  "K": 120.0},
        "Harvest":    {"N": 200.0, "P": 60.0,  "K": 120.0},
    },
    "Tomato": {
        "Sowing":     {"N": 50.0,  "P": 50.0,  "K": 50.0},
        "Germination":{"N": 50.0,  "P": 50.0,  "K": 50.0},
        "Vegetative": {"N": 100.0, "P": 60.0,  "K": 80.0},
        "Flowering":  {"N": 120.0, "P": 60.0,  "K": 100.0},
        "Maturity":   {"N": 120.0, "P": 60.0,  "K": 100.0},
        "Harvest":    {"N": 120.0, "P": 60.0,  "K": 100.0},
    },
    "Soybean": {
        "Sowing":     {"N": 20.0,  "P": 60.0,  "K": 40.0},
        "Germination":{"N": 20.0,  "P": 60.0,  "K": 40.0},
        "Vegetative": {"N": 30.0,  "P": 60.0,  "K": 40.0},
        "Flowering":  {"N": 40.0,  "P": 60.0,  "K": 40.0},
        "Maturity":   {"N": 40.0,  "P": 60.0,  "K": 40.0},
        "Harvest":    {"N": 40.0,  "P": 60.0,  "K": 40.0},
    },
    "Groundnut": {
        "Sowing":     {"N": 20.0,  "P": 40.0,  "K": 40.0},
        "Germination":{"N": 20.0,  "P": 40.0,  "K": 40.0},
        "Vegetative": {"N": 25.0,  "P": 50.0,  "K": 50.0},
        "Flowering":  {"N": 25.0,  "P": 50.0,  "K": 50.0},
        "Maturity":   {"N": 25.0,  "P": 50.0,  "K": 50.0},
        "Harvest":    {"N": 25.0,  "P": 50.0,  "K": 50.0},
    },
    "Mustard": {
        "Sowing":     {"N": 40.0,  "P": 20.0,  "K": 20.0},
        "Germination":{"N": 40.0,  "P": 20.0,  "K": 20.0},
        "Vegetative": {"N": 80.0,  "P": 40.0,  "K": 40.0},
        "Flowering":  {"N": 100.0, "P": 40.0,  "K": 40.0},
        "Maturity":   {"N": 100.0, "P": 40.0,  "K": 40.0},
        "Harvest":    {"N": 100.0, "P": 40.0,  "K": 40.0},
    },
}

NUTRIENT_REQUIREMENT_SOURCE = (
    "Approximate seasonal nutrient requirements derived from ICAR general crop "
    "production guidelines. Expressed as kg/ha (N elemental; P as P₂O₅; K as K₂O). "
    "These values are NOT field-specific. Actual requirements depend on soil test "
    "results, variety, target yield, soil type, and local conditions. "
    "Consult a certified agronomist or ICAR regional extension centre for "
    "field-specific recommendations."
)


def get_nutrient_requirements(
    crop_name: str,
    growth_stage: str,
) -> tuple[dict[str, float] | None, str]:
    """
    Return nutrient requirements for a crop/stage pair.

    Returns ({"N": float, "P": float, "K": float} | None, source_note).
    Returns None if the crop or stage is not in the reference table.
    Case-insensitive matching is attempted.
    """
    # Try exact match first
    req = CROP_NUTRIENT_REQUIREMENTS.get(crop_name, {}).get(growth_stage)
    if req is not None:
        return req, NUTRIENT_REQUIREMENT_SOURCE

    # Case-insensitive fallback
    for stored_crop, stages in CROP_NUTRIENT_REQUIREMENTS.items():
        if stored_crop.lower() == crop_name.lower():
            for stored_stage, vals in stages.items():
                if stored_stage.lower() == growth_stage.lower():
                    return vals, NUTRIENT_REQUIREMENT_SOURCE
            # Crop found but stage missing — return Sowing as conservative default
            default = stages.get("Sowing") or next(iter(stages.values()))
            return default, (
                NUTRIENT_REQUIREMENT_SOURCE
                + f" Growth stage '{growth_stage}' not in reference table; "
                f"using 'Sowing' values as conservative default."
            )

    return None, (
        f"Crop '{crop_name}' is not in the nutrient requirement reference table. "
        "Optimization cannot proceed without validated nutrient targets. "
        "Add crop-specific values or consult an agronomist."
    )
