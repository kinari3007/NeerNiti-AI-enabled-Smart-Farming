# Neer Niti — Next Steps

Prioritized follow-up work. Items in **Backend** require server changes the
frontend cannot do on its own; the frontend is already structured to adopt them.

## High priority — backend gaps that limit the product

1. **User authentication & per-user data isolation.**
   The backend has no users and no auth; data is farm-scoped and any client can
   read any farm by id. To make this a real multi-user product:
   - Add an auth mechanism (JWT/OAuth2, or a hosted provider).
   - Associate farms/recommendations with an owner.
   - Enforce ownership on every read/write.
   - The frontend would then send a token (via the existing central `http`
     client) and the local `session` helper would be replaced by real sessions.
   > The task brief assumed Supabase + user auth + private history. None exist
   > yet — this item is where that work belongs.

2. **Expand the recommendation inputs the model actually uses.**
   The UI only collects fields the backend consumes (soil pH/moisture/OC/EC,
   N-P-K, crop, growth stage, area). Several fields a farmer might expect —
   soil type, season, irrigation type, previous crop, region, previous
   fertilizer/yield — are currently hardcoded defaults / NaN inside
   `backend/app/ml/feature_engineering.py`. To surface them honestly:
   - Wire them through `RecommendationRequest` → feature pipeline so they
     influence the prediction.
   - Then add them to the Analyze wizard (the form is already sectioned for it).

3. **Verified fertilizer prices.**
   Seed prices are `illustrative_sample` / unverified, so the UI must pass
   `allow_unverified_prices` to get a plan and labels them clearly. Import real
   verified prices (admin CSV endpoint exists) or integrate a price source.

## Medium priority — frontend enhancements

4. **Weather panel.** `GET /farms/{id}/weather` is wired in the API layer but
   not yet surfaced as its own UI section. Add a weather card to the dashboard /
   analyze flow for farms that have coordinates.
5. **Crop-selection reuse.** The recommendation request can take a
   `crop_selection_id`; the UI currently sends inline `crop_name`/`growth_stage`.
   Let farmers save and pick stored crop selections.
6. **Delete / manage flows.** Farm delete exists in the API (`farmsApi.remove`,
   with a backend guard when recommendations exist) but has no UI yet.
7. **More tests.** Add component/integration tests (React Testing Library) for
   the Analyze wizard validation and the Recommendation result rendering.

## Housekeeping

8. **Remove the leftover root-level Vite template** (`/src`, root `index.html`,
   root `package.json`, root `eslint.config.js`, `/public`) once confirmed
   unused, to avoid confusion with the real `/frontend` app. _Not removed in
   this pass — needs your confirmation before deleting._
9. **Document the admin workflow** (how to set `ADMIN_API_KEY`, how to import
   prices) for operators.

## Known limitations (carry-over, by design)

- The ML output is a fertilizer **category** suggestion, not a calibrated
  prescription; the UI labels its probability honestly and shows the backend
  disclaimer.
- Nutrient requirements are approximate ICAR reference values, surfaced with
  their source note — not field-calibrated.
