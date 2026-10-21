"""Quick end-to-end smoke test against a running server on localhost:8000."""
import json
import sys
import urllib.request

BASE = "http://localhost:8000/api/v1"
FAILURES = []


def post(url, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    r = urllib.request.urlopen(req)
    return json.loads(r.read())


def get(url):
    r = urllib.request.urlopen(url)
    return json.loads(r.read())


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        FAILURES.append(label)


print("\n=== Neer Niti E2E Smoke Test ===\n")

# --- Health ---
print("[Health]")
h = get("http://localhost:8000/health")
check("health status ok", h["status"] == "ok")

hdb = get("http://localhost:8000/health/db")
check("health/db database connected", hdb["database"] == "connected")
check("health/db ml loaded", hdb["ml_model"] == "loaded")

# --- Crops ---
print("\n[Crops]")
crops = get(f"{BASE}/crops")
check("crops seeded (10)", len(crops) == 10)
crop_names = {c["name"] for c in crops}
check("Wheat in crops", "Wheat" in crop_names)
wheat = next(c for c in crops if c["name"] == "Wheat")

# --- Fertilizers ---
print("\n[Fertilizers]")
ferts = get(f"{BASE}/fertilizers")
check("fertilizers seeded (8)", ferts["total"] == 8)
fert_names = {f["name"] for f in ferts["items"]}
check("Urea in fertilizers", "Urea" in fert_names)
check("DAP in fertilizers", "DAP (Di-ammonium Phosphate)" in fert_names)

# --- Farm CRUD ---
print("\n[Farm CRUD]")
farm = post(f"{BASE}/farms", {
    "name": "Smoke Test Farm",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "area_value": 2.0,
    "area_unit": "hectare",
})
farm_id = farm["id"]
check("farm created", bool(farm_id))
check("farm name correct", farm["name"] == "Smoke Test Farm")

farm_get = get(f"{BASE}/farms/{farm_id}")
check("farm GET works", farm_get["id"] == farm_id)

farms_list = get(f"{BASE}/farms")
check("farm appears in list", any(f["id"] == farm_id for f in farms_list["items"]))

# --- Soil Readings ---
print("\n[Soil Readings]")
reading = post(f"{BASE}/farms/{farm_id}/soil-readings", {
    "collected_at": "2026-10-21T08:00:00+00:00",
    "soil_ph": 7.2,
    "electrical_conductivity": 1.5,
    "ec_unit": "dS/m",
    "soil_moisture": 35.0,
    "moisture_unit": "%",
    "nitrogen": 80.0,
    "phosphorus": 40.0,
    "potassium": 200.0,
    "npk_unit": "mg/kg",
    "data_source": "manual",
})
check("soil reading created", bool(reading["id"]))
check("soil reading validated (no flags)", reading["is_validated"] is True)
check("soil ph stored", reading["soil_ph"] == 7.2)

# Flagged reading (very low pH)
flagged = post(f"{BASE}/farms/{farm_id}/soil-readings", {
    "collected_at": "2026-10-21T09:00:00+00:00",
    "soil_ph": 3.5,
    "data_source": "manual",
})
check("low pH reading accepted (not rejected)", bool(flagged["id"]))
check("low pH reading flagged", flagged["is_validated"] is False)

summary = get(f"{BASE}/farms/{farm_id}/soil-summary")
check("soil summary reading_count = 2", summary["reading_count"] == 2)
check("soil summary ph mean present", summary["ph"] is not None)

# --- Crop Selection ---
print("\n[Crop Selection]")
selection = post(f"{BASE}/farms/{farm_id}/crop-selections", {
    "crop_reference_id": wheat["id"],
    "growth_stage": "Sowing",
    "expected_area_value": 2.0,
    "expected_area_unit": "hectare",
})
check("crop selection created", bool(selection["id"]))
check("crop name populated", selection["crop_name"] == "Wheat")

# --- Recommendation ---
print("\n[Recommendation]")
rec = post(f"{BASE}/farms/{farm_id}/recommendations", {
    "crop_name": "Wheat",
    "growth_stage": "Sowing",
    "area_ha": 2.0,
    "use_weather": False,
    "allow_unverified_prices": True,
})
check("recommendation created", bool(rec["id"]))
check("optimization status feasible", rec["optimization_status"] == "feasible")
check("recommended_fertilizers present", bool(rec["recommended_fertilizers"]))
check("estimated_total_cost > 0", (rec["estimated_total_cost"] or 0) > 0)
check("ml_classifier_suggestion present", rec["ml_classifier_suggestion"] is not None)
check("nutrient_requirements present", rec["nutrient_requirements"] is not None)
check("nutrient_balance present", rec["nutrient_balance"] is not None)

if rec["recommended_fertilizers"]:
    print("\n  Optimized fertilizer plan:")
    for item in rec["recommended_fertilizers"]:
        print(
            f"    {item['product_name']:30s} "
            f"{item['quantity_kg_total']:7.1f} kg total  "
            f"@ {item['price_per_kg']:.2f}/kg  "
            f"= {item['cost_total']:.2f} {item['currency']}"
        )
    print(f"\n  TOTAL COST: {rec['estimated_total_cost']:.2f} {rec['cost_currency']}")

if rec["nutrient_balance"]:
    nb = rec["nutrient_balance"]
    print(f"\n  Nutrient balance:")
    print(f"    N  required {nb['n_required_kg_per_ha']:.1f}  supplied {nb['n_supplied_kg_per_ha']:.2f} kg/ha")
    print(f"    P₂O₅ required {nb['p_required_kg_per_ha']:.1f}  supplied {nb['p_supplied_kg_per_ha']:.2f} kg/ha")
    print(f"    K₂O  required {nb['k_required_kg_per_ha']:.1f}  supplied {nb['k_supplied_kg_per_ha']:.2f} kg/ha")

print(f"\n  ML suggestion: {rec['ml_classifier_suggestion']['predicted_class'] if rec['ml_classifier_suggestion'] else 'none'}")
print(f"  Warnings ({len(rec['warnings'])}): {rec['warnings'][:2]}")

# --- Recommendation retrieve ---
rec2 = get(f"{BASE}/recommendations/{rec['id']}")
check("recommendation GET by ID works", rec2["id"] == rec["id"])

rec_list = get(f"{BASE}/farms/{farm_id}/recommendations")
check("recommendation appears in farm list", any(r["id"] == rec["id"] for r in rec_list))

# --- Infeasible case ---
print("\n[Infeasibility detection]")
# Create a crop not in the reference table to trigger skipped_no_requirements
rec_no_crop = post(f"{BASE}/farms/{farm_id}/recommendations", {
    "crop_name": "UnknownCrop999",
    "growth_stage": "Sowing",
    "area_ha": 1.0,
    "use_weather": False,
    "allow_unverified_prices": True,
})
check(
    "unknown crop → skipped_no_requirements",
    rec_no_crop["optimization_status"] == "skipped_no_requirements",
)

# --- Results ---
print(f"\n{'='*50}")
if FAILURES:
    print(f"RESULT: {len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
else:
    print(f"RESULT: ALL CHECKS PASSED")
    sys.exit(0)
