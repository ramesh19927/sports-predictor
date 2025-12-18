# Copilot / AI agent instructions — Sports Predictor

Be concise and make minimal, focused changes. This project is a small local-first prediction stack (FastAPI backend, Vite web, Expo mobile). Below are the essential facts and actionable patterns to be productive immediately.

- **Big picture**: ingestion -> analyst aggregation -> prediction engine -> repository -> REST API. The backend seeds sample data and exposes predictions to the web/mobile frontends. See [README.md](README.md) for the architecture diagram.

- **Core backend files**:
  - Settings and logger: [backend/app/config.py](backend/app/config.py)
  - FastAPI app + routes: [backend/app/main.py](backend/app/main.py)
  - Pydantic models: [backend/app/models/prediction.py](backend/app/models/prediction.py)
  - Ingestion providers (stubs): [backend/app/services/ingestion.py](backend/app/services/ingestion.py)
  - Analyst aggregation: [backend/app/services/analyst.py](backend/app/services/analyst.py)
  - Prediction logic: [backend/app/services/prediction_engine.py](backend/app/services/prediction_engine.py)
  - Persistence: [backend/app/services/repository.py](backend/app/services/repository.py)

- **How data flows** (code pointers):
  - `main._hydrate_sample_predictions()` (in `main.py`) calls `DataIngestionService.ingest_all()` -> `AnalystAggregator.aggregate()` -> `PredictionEngine.predict()` -> `PredictionRepository.save_many()` which writes to `backend/app/data/sample_predictions.json`.
  - To add real providers, implement functions returning the same payload shape as `_load_*_stub()` and register them in `DataIngestionService.providers`.

- **API surface** (examples):
  - `GET /api/predictions` — supports filters: `sport`, `league`, `market_type`, `confidence` (mapped to `ConfidenceTier`), `date_from`, `date_to` (see [main.py](backend/app/main.py)).
  - `GET /api/predictions/{id}` — returns a single `Prediction` (404 if missing).
  - `GET /api/events/week` and `/api/events/weekend` — return grouped `EventSummary` objects.

- **Project-specific conventions & patterns**:
  - Pydantic models are authoritative for JSON shape; use `Prediction`/`EventSummary`/`AnalystSignal` in any new endpoints.
  - Time handling uses UTC and `datetime.utcnow()`; persisted `event_date` is ISO-formatted (see `PredictionRepository.load/save_many`).
  - The repo is file-backed and keeps an in-memory cache (`PredictionRepository._predictions`). Mutating behavior occurs in `save_many()` — consider clearing/controlling cache when adding persistence.
  - Prediction weights are explicit in `PredictionEngine.__init__` (base_model_weight, analyst_weight, context_weight). Tune there for behaviour changes.

- **Dev & run commands (verified in README)**:
  - Full stack (recommended): `docker-compose up` (root). Backend at `http://localhost:8000`.
  - Backend only: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000`
  - Web: `cd web && npm install && npm run dev -- --host 0.0.0.0 --port 5173` (set `VITE_API_BASE` to override API URL).
  - Mobile (Expo): `cd mobile && npm install && npm start` (update `app.json` `expo.extra.apiBase` if needed).

- **Environment / configuration**:
  - All settings use `pydantic.BaseSettings` with prefix `SPORTS_PREDICTOR_` (see `get_settings()` in `config.py`). Important vars:
    - `SPORTS_PREDICTOR_API_PREFIX` (default `/api`)
    - `SPORTS_PREDICTOR_LOG_LEVEL` (default `INFO`)
    - `SPORTS_PREDICTOR_DEFAULT_CONFIDENCE_THRESHOLD`
  - Frontends read `VITE_API_BASE` (web) and `expo.extra.apiBase` (mobile) to locate the backend.

- **Where to make common changes** (quick map):
  - Add ingestion provider: `backend/app/services/ingestion.py` (follow `_load_*_stub()` shapes).
  - Change prediction algorithm / weights: `backend/app/services/prediction_engine.py` (see `_base_probability_from_form`, `_injury_adjustment`).
  - Add fields to models: update `backend/app/models/prediction.py` and adjust `PredictionRepository` serialization accordingly.
  - Add new API route: add path to `backend/app/main.py` and reference Pydantic models in `response_model`.

- **Testing & debugging tips** (project-specific):
  - Use the seeded file `backend/app/data/sample_predictions.json` to craft request payloads and verify filters. The backend hydrates this file on startup if empty.
  - Logging is configured in `get_logger()`; change `SPORTS_PREDICTOR_LOG_LEVEL` or call `get_logger(__name__)` in new modules for consistent logs.

If anything here is unclear or you'd like more examples (e.g., adding a new ingestion provider or extending `Prediction`), tell me what to expand and I'll iterate.
