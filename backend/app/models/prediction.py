from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ConfidenceTier(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class PredictionSourceMix(BaseModel):
    analyst: float = Field(..., description="Contribution from analyst aggregation (0-1)")
    model: float = Field(..., description="Contribution from internal model (0-1)")
    context: float = Field(..., description="Contribution from contextual adjustments (0-1)")


class Prediction(BaseModel):
    id: str
    sport: str
    league: str
    event: str
    event_date: datetime
    market_type: str
    prediction: str
    probability: float = Field(..., ge=0, le=100)
    confidence_tier: ConfidenceTier
    source_mix: PredictionSourceMix
    factors: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EventSummary(BaseModel):
    sport: str
    league: str
    event: str
    event_date: datetime
    predictions: List[Prediction]


class AnalystSignal(BaseModel):
    analyst: str
    credibility: float
    market_view: Dict[str, float]
    notes: Optional[str]


class IngestionRecord(BaseModel):
    source: str
    captured_at: datetime
    payload: Dict[str, object]
