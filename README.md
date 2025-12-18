# Sports Predictor

Local-first sports prediction stack that ingests fixture and context data, aggregates analyst signals, and exposes structured predictions to web and mobile clients.

## System architecture
```
                   +-----------------------+
                   |   Data sources (APIs) |
                   +-----------------------+
                               |
                     [Data ingestion layer]
                               |
                +--------------+--------------+
                | Analyst aggregation (weights)|
                +--------------+--------------+
                               |
                     [Prediction engine]
                               |
                        Prediction repo
                               |
         +---------------------+----------------------+
         |                                            |
   FastAPI backend (REST)                       Observability/logging
         |                                            |
   +-----+------+                            +--------+-------+
   |            |                            |                |
React web app   |                            |      Mobile (Expo RN)
   |            |                            |                |
 Local dev via Vite                   Local dev via Expo client
```

## Backend (FastAPI)
- Endpoints:
  - `GET /health`
  - `GET /api/predictions` (filters: `sport`, `league`, `market_type`, `confidence`, `date_from`, `date_to`)
  - `GET /api/predictions/{id}`
  - `GET /api/events/week` and `/api/events/weekend`
- Services:
  - `DataIngestionService`: pluggable providers for fixtures, form, injuries, weather.
  - `AnalystAggregator`: normalizes analyst projections with credibility weights.
  - `PredictionEngine`: combines form, injuries, weather, and analyst blend into probabilities and confidence tiers.
  - `PredictionRepository`: simple JSON-backed storage for predictions.
- Config via env vars (prefixed `SPORTS_PREDICTOR_`), no hardcoded keys.
- Logging controlled by `SPORTS_PREDICTOR_LOG_LEVEL` (defaults to `INFO`).

## Web app (React + Vite)
- Weekly/weekend-ready grid with sortable probabilities and filters (sport, league, market, confidence).
- Event drawer shows per-event predictions, factors, and source mix.
- Points to the local FastAPI backend; override via `VITE_API_BASE`.

## Mobile app (Expo React Native)
- Cross-platform list of events with inline predictions and quick filters.
- Reads backend base URL from `app.json` (`extra.apiBase`).

## Sample predictions
Seeded for three sports:
- Soccer (EPL)
- American football (NFL)
- Basketball (NBA)

Markets include moneyline, player props, team props, and event props with probability and confidence tiers.

## Local setup
### Prerequisites
- Docker + Docker Compose (recommended), or Python 3.11, Node 20+, and npm.

### One-command stack (backend + web)
```bash
docker-compose up
```
- Backend: http://localhost:8000
- Web: http://localhost:5173 (connects to backend)

### Backend only (manual)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Web app (manual)
```bash
cd web
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### Mobile app (manual)
```bash
cd mobile
npm install
npm start   # opens Expo dev tools; ensure backend reachable at apiBase
```

## Environment variables
- `SPORTS_PREDICTOR_LOG_LEVEL`: Logging level (default `INFO`).
- `SPORTS_PREDICTOR_API_PREFIX`: API prefix (default `/api`).
- Web: `VITE_API_BASE` to override API URL (default `http://localhost:8000/api`).
- Mobile: update `app.json` `expo.extra.apiBase` as needed.

## How predictions are generated
1. Ingestion stubs load fixtures, form, injuries, and weather (replaceable providers).
2. Analyst signals are normalized and weighted.
3. Prediction engine blends model baseline (form), analyst weight, and context (injuries/weather) to produce probabilities and confidence tiers.
4. Results are persisted to `backend/app/data/sample_predictions.json` and served via REST.

## Known limitations
- Ingestion uses stub data; wire real APIs via new providers.
- Persistence is file-based; replace with a database for multi-user scaling.
- Models are heuristic; plug in ML pipelines behind `PredictionEngine`.
- No authentication; add API keys or OAuth for production.
