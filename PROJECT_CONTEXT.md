# Neer Niti — Project Context

_Last updated by the frontend QA/integration pass._

Neer Niti ("AgriSense" in the UI) is an AI-assisted smart-farming application that
gives farmers a **cost-optimized fertilizer recommendation** from their soil
measurements, crop, and local weather.

## Repository layout

```
/backend        FastAPI backend (Python 3.14, async SQLAlchemy, SQLite dev DB)
/frontend       React 19 + Vite 8 single-page app (the real UI)
/ml             ML training script + trained classifier artifacts
/data           Training dataset (fertilizer_recommendation.csv)
/scripts        e2e_smoke_test.py — live backend contract check
/src, /index.html, /package.json   LEFTOVER root-level Vite template — NOT the app
```

> Note: a stray Vite starter template still lives at the repository root
> (`/src`, root `index.html`, root `package.json`). It is unused. The real
> frontend is the `/frontend` folder. See NEXT_STEPS.md.

## Backend (already implemented — not changed in this pass)

- FastAPI app, all business routes under `/api/v1`, health at `/health`.
- SQLite via `aiosqlite` for local dev; `DATABASE_URL` switches to PostgreSQL.
- A trained `RandomForestClassifier` (`ml/artifacts/fertilizer_classifier.pkl`,
  version 1.0.0, test macro-F1 ≈ 0.75) predicts a fertilizer **category**.
- A SciPy linear-programming optimizer produces the cost-minimizing fertilizer
  plan that meets ICAR reference nutrient targets.
- Weather comes from Open-Meteo using the farm's coordinates.

### Authentication (important)

- There is **no user authentication and no Supabase** in this project.
- The only credential is an `X-API-Key` header that guards two **admin** endpoints
  (create fertilizer product, import prices via CSV). The farmer-facing UI never
  calls those, so the app needs no key.
- Data is scoped to **farms**, not users. Any client that knows a farm's id can
  read that farm. There is no per-user data isolation. (See PROJECT_AUDIT.md.)

## Frontend

- React 19, React Router 7, plain CSS with a design-token system. No CSS framework.
- Dev server proxies `/api` and `/health` to `http://localhost:8000`
  (`frontend/vite.config.js`).
- API base URL is configurable with `VITE_API_BASE_URL` (optional, non-secret;
  see `frontend/.env.example`). Default is the relative `/api/v1`.
- The farmer's display name and active farm are stored in `localStorage`
  (honest device-local convenience, **not** a security boundary).

### Pages (`frontend/src/pages`)

| Route | Page | Purpose |
|-------|------|---------|
| `/` | `landing/LandingPage` | Marketing landing (hero, challenge, how-it-works, why-us, soil health, CTA, footer) |
| `/app` | `app/DashboardPage` | Greeting banner, Analyze CTA, soil overview, recent recommendations, quick nav |
| `/app/analyze` | `app/analyze/AnalyzePage` | 3-step wizard: Farm → Soil → Crop & options → generate recommendation |
| `/app/recommendations/:id` | `app/RecommendationPage` | Recommendation result: ML suggestion, optimized plan, nutrient balance, warnings |
| `/app/history` | `app/HistoryPage` | Past recommendations with search + status filter |
| `/app/profile` | `app/ProfilePage` | Farmer name + editable farm details (PATCH) + sign-out |

### Reusable components (`frontend/src/components`)

- **ui/**: `Button`, `Card`, `SectionHeading`, `StepItem`, `StatPill`,
  `OrganicImage`, `Field`/`Input`/`Select`/`Textarea`, `Feedback`
  (`Spinner`, `Skeleton`, `SkeletonCard`, `Badge`), `States`
  (`EmptyState`, `ErrorState`), `ToastProvider`/`useToast`, `Modal`/`ConfirmDialog`.
- **layout/**: `AppLayout`, `Sidebar`, `TopBar`.
- **app/**: `PageHeader`, `FarmSwitcher`, `Stepper`, `RecommendationCard`,
  `SoilSummaryGrid`.
- **context/**: `FarmProvider` + `useFarm` (`farm-context.js`).
- **assets/illustrations/**: original SVG scenes (`HeroScene`, `PlantingScene`,
  `SoilHealthScene`, `FarmerExamineScene`) + `decor` icons.

### API service layer (`frontend/src/api`)

Centralized `http` client (`client.js`) with an `ApiError` type, plus one module
per domain: `farms`, `soil`, `crops`, `recommendations`, `weather`
(+ fertilizers), and a `session` helper.

## How to run

```bash
# Backend (terminal 1)
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend (terminal 2)
cd frontend
npm install
npm run dev        # http://localhost:5173  (proxies API to :8000)
```

Build / lint / test:

```bash
cd frontend
npm run build
npm run lint
npm test
```
