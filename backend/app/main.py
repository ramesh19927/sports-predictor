from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models.prediction import ConfidenceTier, EventSummary, Prediction
from .services.analyst import AnalystAggregator
from .services.ingestion import DataIngestionService
from .services.prediction_engine import PredictionEngine, PredictionInputs
from .services.repository import PredictionRepository

settings = get_settings()
app = FastAPI(title="Sports Predictor", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).parent / "data" / "sample_predictions.json"
repo = PredictionRepository(DATA_PATH)


def _hydrate_sample_predictions():
    if repo.list():
        return
    ingestion = DataIngestionService()
    records = ingestion.ingest_all()
    fixtures = records[0].payload["events"]
    form = records[1].payload
    injuries = records[2].payload
    weather = records[3].payload
    analyst = AnalystAggregator()
    signals = analyst.aggregate([])
    engine = PredictionEngine()
    predictions: List[Prediction] = []
    for fixture in fixtures:
        inputs = PredictionInputs(
            fixture=fixture,
            form=form,
            injuries=injuries,
            weather=weather,
            analyst_mix=signals,
        )
        predictions.extend(engine.predict(inputs))
    repo.save_many(predictions)


def get_repository():
    _hydrate_sample_predictions()
    return repo


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.get(f"{settings.api_prefix}/predictions", response_model=List[Prediction])
def list_predictions(
    sport: Optional[str] = None,
    league: Optional[str] = None,
    market_type: Optional[str] = None,
    confidence_tier: Optional[ConfidenceTier] = Query(None, alias="confidence"),
    start_date: Optional[datetime] = Query(None, alias="date_from"),
    end_date: Optional[datetime] = Query(None, alias="date_to"),
    repo: PredictionRepository = Depends(get_repository),
):
    return repo.filter(
        sport=sport,
        league=league,
        market_type=market_type,
        confidence_tier=confidence_tier,
        date_from=start_date,
        date_to=end_date,
    )


@app.get(f"{settings.api_prefix}/predictions/{{prediction_id}}", response_model=Prediction)
def get_prediction(prediction_id: str, repo: PredictionRepository = Depends(get_repository)):
    prediction = repo.get(prediction_id)
    if not prediction:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction


@app.get(f"{settings.api_prefix}/events/week", response_model=List[EventSummary])
def get_week_events(repo: PredictionRepository = Depends(get_repository)):
    now = datetime.utcnow()
    end = now + timedelta(days=7)
    return _group_events(repo, now, end)


@app.get(f"{settings.api_prefix}/events/weekend", response_model=List[EventSummary])
def get_weekend_events(repo: PredictionRepository = Depends(get_repository)):
    now = datetime.utcnow()
    saturday = now + timedelta((5 - now.weekday()) % 7)
    sunday = saturday + timedelta(days=1)
    return _group_events(repo, saturday, sunday)


def _group_events(repo: PredictionRepository, start: datetime, end: datetime) -> List[EventSummary]:
    predictions = repo.filter(date_from=start, date_to=end)
    events = {}
    for prediction in predictions:
        key = (prediction.event, prediction.event_date)
        events.setdefault(key, []).append(prediction)
    summaries = [
        EventSummary(
            sport=group[0].sport,
            league=group[0].league,
            event=event,
            event_date=date,
            predictions=group,
        )
        for (event, date), group in events.items()
    ]
    return sorted(summaries, key=lambda e: e.event_date)
