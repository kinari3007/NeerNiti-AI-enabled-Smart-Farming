# Neer Niti — Frontend Integration & QA Audit

_Scope: integration and quality-assurance pass on the `/frontend` React app and
its wiring to the existing FastAPI backend. The backend was inspected but not
modified._

## 1. Backend integration — verified

Every frontend API call maps to a **real, existing** backend endpoint. No
endpoints were invented, no responses faked, no recommendations hardcoded.

| Frontend call | Backend route | Verified |
|---|---|---|
| `farmsApi.list/get/create/update/remove` | `GET/POST /api/v1/farms`, `GET/PATCH/DELETE /api/v1/farms/{id}` | ✅ |
| `soilApi.createReading/listReadings` | `POST/GET /api/v1/farms/{id}/soil-readings` | ✅ |
| `soilApi.summary` | `GET /api/v1/farms/{id}/soil-summary` | ✅ |
| `cropsApi.list/get` | `GET /api/v1/crops`, `/crops/{id}` | ✅ |
| `cropsApi.createSelection/listSelections` | `POST/GET /api/v1/farms/{id}/crop-selections` | ✅ |
| `weatherApi.forFarm` | `GET /api/v1/farms/{id}/weather` | ✅ |
| `fertilizersApi.list/get/prices` | `GET /api/v1/fertilizers`, `/fertilizers/{id}`, `/fertilizers/prices` | ✅ |
| `recommendationsApi.create/listForFarm/get` | `POST/GET /api/v1/farms/{id}/recommendations`, `GET /api/v1/recommendations/{id}` | ✅ |
| `http.health` | `GET /health` | ✅ |

Request/response shapes match the backend Pydantic schemas (confirmed by reading
`backend/app/schemas/*` and the ML feature pipeline).

### Live integration test — executed

`scripts/e2e_smoke_test.py` was run against a **live** backend (uvicorn on
:8000, ML model loaded, DB seeded):

```
RESULT: ALL CHECKS PASSED   (28 checks)
```

It exercised the full farmer flow end to end, including a real recommendation:
- ML suggestion: `Compost`
- Optimized plan: Urea 260.9 kg + MOP 100 kg + SSP 375 kg = **₹6,075.54**
- Nutrient balance met exactly (N 60 / P₂O₅ 30 / K₂O 30 kg/ha)
- Infeasible case detected (unknown crop → `skipped_no_requirements`)

## 2. Authentication & security

| Checked | Finding |
|---|---|
| Supabase usage | **None.** Zero references anywhere in the repo. |
| User authentication | **Not implemented** in the backend. |
| Admin protection | `X-API-Key` header guards only `POST /fertilizers` and `/fertilizers/prices/import`. The farmer UI never calls these. |
| Secrets in frontend | **None.** No keys; API base URL is a public, optional env var. |
| Per-user data isolation | **Not enforced by the backend** — data is farm-scoped; any client can read any farm by id. Documented as a backend gap, not faked in the UI. |

Frontend robustness added/confirmed:
- `ApiError` exposes `isAuthError` (401/403), `isNotFound` (404),
  `isNetworkError` (0) for honest, specific messaging.
- `FarmProvider` reconciles a stale stored farm id (falls back to first farm or
  none) — the closest honest equivalent to "expired session" handling here.
- `RecommendationPage` handles 404 / missing recommendations with a retry state.
- `ProfilePage` states plainly that there are no server-side accounts and that
  name/active-farm live only on the device.

> The task brief referenced Supabase, service-role keys, user auth, and
> per-user private history. **None of those exist in this codebase.** They are
> recorded as future backend work in NEXT_STEPS.md rather than simulated.

## 3. Visual quality (vs reference image)

| Aspect | Status |
|---|---|
| Sidebar proportions (dark forest-green, 248px, brand top, quote bottom) | ✅ matches |
| Hero illustration placement (rounded panel, farmer bleed-right, dark overlay) | ✅ matches |
| Typography (Lora headings, DM Sans body) | ✅ matches |
| Color palette (forest/deep green, cream, gold, sage) | ✅ consistent, token-driven |
| Card design (large radii, soft warm shadows) | ✅ matches |
| Whitespace & hierarchy | ✅ generous, proportional |
| Buttons (pill, primary/gold/ghost) | ✅ matches |
| Illustrations | Original hand-authored SVG scenes, visually consistent |

## 4. Responsive behavior

- Breakpoints at 900px (sidebar → mobile drawer with scrim; dashboard banner art
  hides) and 560px (form grids and action rows stack).
- Forms use value+unit paired fields that collapse cleanly; cards reflow via
  `auto-fill` grids; the wizard stepper hides labels on small screens.

## 5. Technical checks — actually executed

| Check | Command | Result |
|---|---|---|
| Production build | `npm run build` | ✅ EXIT 0 — 107 modules, 43.7 kB CSS / 341 kB JS |
| Lint | `npx eslint .` | ✅ EXIT 0 — 0 problems |
| Unit tests | `npm test` | ✅ 20/20 passing (Vitest) |
| Live API contract | `python scripts/e2e_smoke_test.py` | ✅ 28/28 passing |

Tests added this pass:
- `frontend/src/utils/format.test.js` — 13 tests (money/number/percent/date/JSON).
- `frontend/src/api/client.test.js` — 7 tests (URL prefixing, JSON handling,
  error mapping, `ApiError` classifiers, network-error wrapping, health path).

## 6. Fixes applied this pass

- Made the API base URL configurable via `VITE_API_BASE_URL` (kept `/api/v1`
  default + Vite proxy); added `frontend/.env.example`.
- Added `ApiError.isAuthError/isNotFound/isNetworkError`.
- Split `useFarm`/`FarmContext` into `frontend/src/context/farm-context.js` so
  `FarmProvider.jsx` exports only a component — resolved the Vite Fast Refresh
  warning and removed a lint-disable. Updated 6 import sites.
- Set up Vitest + jsdom and wrote the first two test suites.

## 7. What was NOT changed

- The backend (no code changes).
- The leftover root-level Vite template (`/src`, root config files).
- Git history; nothing was committed, pushed, or deployed.
