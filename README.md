# Neer Niti — AI-Enabled Smart Farming Backend

Cost-optimised fertilizer recommendation system for Indian farmers.

---

## Overview

Neer Niti combines soil measurements, weather data, crop requirements, and fertilizer pricing to recommend the **minimum-cost fertilizer combination** that meets validated crop nutrient needs.

The system has three distinct output layers — never conflated:

| Layer | What it does |
|-------|-------------|
| **ML Classifier** | Suggests a fertilizer *category* (Urea, DAP, MOP…) based on input features. Statistical suggestion only — not a nutrient prescription. |
| **Nutrient Requirements** | Approximate per-crop, per-stage values from ICAR general guidelines. Not field-calibrated. |
| **LP Optimizer** | Finds the lowest-cost fertilizer mix that meets the nutrient targets. Globally optimal for the linear formulation (HiGHS solver). |

---

## Architecture

```
backend/
  app/
    api/routes/       — FastAPI route handlers (health, farms, soil, crops,
                        weather, fertilizers, recommendations)
    core/             — Config, logging, exceptions, admin API-key auth
    db/               — SQLAlchemy async engine, session, init_db
    models/           — ORM models (Farm, SoilReading, Crop, Fertilizer,
                        FertilizerPrice, Recommendation)
    schemas/          — Pydantic request/response models
    services/         — Business logic (farm, soil, weather, crop, fertilizer,
                        recommendation)
    ml/               — Model loader, feature engineering, classifier inference
    optimization/     — Nutrient conversions, crop reference table, LP solver
  tests/              — pytest test suite (70 tests)
  requirements.txt
  pytest.ini

ml/
  src/models/train_classifier.py  — Training script
  artifacts/                      — Trained model, label encoder, metadata

data/
  raw/fertilizer_recommendation.csv  — 10,000-row training dataset
```

---

## Prerequisites

- Python 3.11+ (tested on 3.14)
- pip

No Docker required for local development.

---

## Installation

```bash
cd backend
pip install -r requirements.txt
```

---

## Environment Configuration

```bash
cp .env.example .env
# Edit .env — at minimum change ADMIN_API_KEY
```

Key variables:

| Variable | Default | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./neerniti.db` | Switch to `postgresql+asyncpg://...` for production |
| `ADMIN_API_KEY` | `change-me-in-production` | **Must be changed.** Protects admin endpoints. |
| `WEATHER_API_BASE_URL` | Open-Meteo URL | No API key needed |
| `ML_MODEL_PATH` | `ml/artifacts/fertilizer_classifier.pkl` | Relative to repo root |

---

## Database Setup

Tables are created automatically on first startup (SQLite).

For PostgreSQL, use Alembic:
```bash
cd backend
alembic init alembic          # first time only
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

## ML Model Training

The training script must be run once before the ML classifier is available:

```bash
# From repo root
python ml/src/models/train_classifier.py
```

**Actual training results (verified):**
- Dataset: 10,000 rows, 7 classes
- Test accuracy: **87.5%**
- Test macro F1: **0.7513**
- 5-fold CV macro F1: **0.7623 ± 0.0099**

Known limitation: SSP class has low precision (0.15) due to class imbalance (182/10,000 samples). Documented in `ml/artifacts/model_metadata.json`.

---

## Starting the Server

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

On first startup the server will:
1. Load the ML model
2. Create database tables
3. Seed the crop reference catalogue (10 crops)
4. Seed 8 standard fertilizer products with **illustrative sample prices**

**API documentation:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

---

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness probe |
| GET | `/health/db` | Database + ML model status |

### Farms
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/farms` | Create a farm |
| GET | `/api/v1/farms` | List farms (paginated) |
| GET | `/api/v1/farms/{id}` | Get a farm |
| PATCH | `/api/v1/farms/{id}` | Update a farm |
| DELETE | `/api/v1/farms/{id}` | Delete (blocked if recommendations exist) |

### Soil
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/farms/{id}/soil-readings` | Submit a soil measurement |
| GET | `/api/v1/farms/{id}/soil-readings` | List readings |
| GET | `/api/v1/farms/{id}/soil-summary` | Aggregated statistics |

### Crops
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/crops` | Supported crop catalogue |
| GET | `/api/v1/crops/{id}` | Get a crop |
| POST | `/api/v1/farms/{id}/crop-selections` | Record a crop on a farm |
| GET | `/api/v1/farms/{id}/crop-selections` | List crop selections |

### Weather
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/farms/{id}/weather` | Current + 7-day forecast (requires farm coordinates) |

### Fertilizers
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/fertilizers` | — | List products |
| GET | `/api/v1/fertilizers/{id}` | — | Get product |
| GET | `/api/v1/fertilizers/prices` | — | List prices |
| POST | `/api/v1/fertilizers` | `X-API-Key` | Create product |
| POST | `/api/v1/fertilizers/prices/import` | `X-API-Key` | Import prices from CSV |

### Recommendations
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/farms/{id}/recommendations` | Generate recommendation |
| GET | `/api/v1/farms/{id}/recommendations` | List recommendations |
| GET | `/api/v1/recommendations/{id}` | Get recommendation |

---

## Fertilizer Price Import (CSV)

```bash
curl -X POST http://localhost:8000/api/v1/fertilizers/prices/import \
  -H "X-API-Key: your-admin-key" \
  -F "file=@prices.csv"
```

CSV format (header required):
```
product_name,price_value,currency,price_unit,supplier,location,source,is_verified,bag_weight_kg
Urea,6.50,INR,INR/kg,State Cooperative,Agra UP,verified_market,true,
DAP (Di-ammonium Phosphate),28.00,INR,INR/bag,IFFCO,Delhi,csv_import,false,50
```

Use `source=verified_market` and `is_verified=true` only for prices you have confirmed against a real market source.

---

## Example: Generate a Recommendation

```bash
# 1. Create a farm
curl -X POST http://localhost:8000/api/v1/farms \
  -H "Content-Type: application/json" \
  -d '{"name":"My Farm","latitude":28.61,"longitude":77.20,"area_value":2,"area_unit":"hectare"}'

# 2. Submit a soil reading
curl -X POST http://localhost:8000/api/v1/farms/{farm_id}/soil-readings \
  -H "Content-Type: application/json" \
  -d '{
    "collected_at":"2026-10-21T08:00:00+00:00",
    "soil_ph":7.2, "electrical_conductivity":1.5, "ec_unit":"dS/m",
    "nitrogen":80, "phosphorus":40, "potassium":200, "npk_unit":"mg/kg",
    "data_source":"manual"
  }'

# 3. Generate a recommendation (uses illustrative sample prices)
curl -X POST http://localhost:8000/api/v1/farms/{farm_id}/recommendations \
  -H "Content-Type: application/json" \
  -d '{"crop_name":"Wheat","growth_stage":"Sowing","area_ha":2.0,"allow_unverified_prices":true}'
```

**Example response (Wheat Sowing, 2 ha):**
- Urea: 261 kg total @ ₹5.80/kg = ₹1,513
- MOP: 100 kg total @ ₹17.50/kg = ₹1,750
- SSP: 375 kg total @ ₹7.50/kg = ₹2,813
- **Total: ₹6,076** — N/P₂O₅/K₂O targets exactly met

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

**Actual results: 70 tests pass, 0 failures.**

Test coverage:
- Health endpoints
- Farm CRUD and validation
- Soil reading validation, flagging, and aggregation
- Mixed-unit rejection in soil summary
- Fertilizer products and prices (including CSV import)
- Admin key authentication
- Nutrient unit conversions (N, P₂O₅, K₂O)
- LP optimizer (feasible, infeasible, zero-price exclusion)
- Full recommendation pipeline
- Weather mocking and cache behaviour
- Price provenance in recommendations
- Infeasibility detection

---

## Known Limitations

1. **Nutrient requirements are approximate** — sourced from ICAR general guidelines, not field-calibrated. Always consult a certified agronomist.

2. **ML classifier is category-only** — predicts which fertilizer type (Urea, DAP…), not quantities or application rates. SSP class has low precision due to class imbalance.

3. **Seed prices are illustrative** — all prices seeded at startup are marked `source=illustrative_sample, is_verified=false`. Import real prices via the CSV endpoint.

4. **No user authentication** — admin endpoints use a single API key (`X-API-Key`). Not suitable for multi-user public deployment without adding proper auth.

5. **Irrigation water pH** — stored and surfaced in warnings when acidic/alkaline, but does not automatically adjust fertilizer recommendations (no validated correction formula implemented).

6. **No production HTTPS/reverse proxy config** — run behind nginx or a cloud load balancer in production.

---

## Agricultural Validation Assumptions

- Nutrient requirements (N as elemental, P as P₂O₅, K as K₂O) are from ICAR general crop production guidelines.
- Fertilizer compositions follow Indian fertilizer label convention (P as P₂O₅, K as K₂O).
- LP objective: minimise total cost subject to meeting ≥ nutrient targets. Upper bound of 500 kg/ha per product prevents agronomically unsafe quantities.
- Weather data informs the ML classifier as an input feature. It is not directly converted into nutrient adjustments.
- Soil test correction (subtracting available nutrients already in soil) is not implemented — a future enhancement requiring validated soil-to-nutrient conversion factors.
