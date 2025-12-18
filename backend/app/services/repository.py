from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from ..config import get_logger
from ..models.prediction import Prediction

logger = get_logger(__name__)


class PredictionRepository:
    """Simple file-backed repository for sample predictions."""

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self._predictions: List[Prediction] = []

    def load(self) -> List[Prediction]:
        if self._predictions:
            return self._predictions
        with self.data_path.open() as f:
            raw = json.load(f)
        self._predictions = [Prediction(**{**p, "event_date": datetime.fromisoformat(p["event_date"])}) for p in raw]
        logger.info("Loaded %d seeded predictions", len(self._predictions))
        return self._predictions

    def list(self) -> List[Prediction]:
        return self.load()

    def save_many(self, predictions: List[Prediction]):
        self._predictions.extend(predictions)
        with self.data_path.open("w") as f:
            payload = [p.copy(update={"event_date": p.event_date.isoformat()}) for p in self._predictions]
            json.dump(payload, f, indent=2)
        logger.info("Persisted %d predictions", len(self._predictions))

    def get(self, prediction_id: str) -> Prediction | None:
        return next((p for p in self.load() if p.id == prediction_id), None)

    def filter(self, **filters) -> List[Prediction]:
        def matches(pred: Prediction) -> bool:
            sport = filters.get("sport")
            league = filters.get("league")
            market_type = filters.get("market_type")
            confidence = filters.get("confidence_tier")
            date_from = filters.get("date_from")
            date_to = filters.get("date_to")

            if sport and pred.sport.lower() != sport.lower():
                return False
            if league and pred.league.lower() != league.lower():
                return False
            if market_type and pred.market_type.lower() != market_type.lower():
                return False
            if confidence and pred.confidence_tier != confidence:
                return False
            if date_from and pred.event_date < date_from:
                return False
            if date_to and pred.event_date > date_to:
                return False
            return True

        results = [p for p in self.load() if matches(p)]
        logger.debug("Filtered to %d predictions", len(results))
        return results
