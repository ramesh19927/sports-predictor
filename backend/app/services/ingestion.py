from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from ..config import get_logger
from ..models.prediction import IngestionRecord

logger = get_logger(__name__)


class DataIngestionService:
    """Collects fixture, form, injury, and contextual data from multiple sources.

    The current version uses static sample payloads, but the interface is built so
    new providers can be added behind the `providers` mapping.
    """

    def __init__(self, providers: Dict[str, callable] | None = None):
        self.providers = providers or {
            "fixtures": self._load_fixture_stub,
            "form": self._load_form_stub,
            "injuries": self._load_injury_stub,
            "weather": self._load_weather_stub,
        }

    def ingest_all(self) -> List[IngestionRecord]:
        records: List[IngestionRecord] = []
        for name, provider in self.providers.items():
            payload = provider()
            record = IngestionRecord(source=name, captured_at=datetime.utcnow(), payload=payload)
            logger.info("Ingested payload from %s", name)
            records.append(record)
        return records

    def _load_fixture_stub(self):
        now = datetime.utcnow()
        return {
            "events": [
                {
                    "id": "soccer-arsenal-spurs",
                    "sport": "soccer",
                    "league": "EPL",
                    "home": "Arsenal",
                    "away": "Tottenham",
                    "event_date": now + timedelta(days=2),
                },
                {
                    "id": "nfl-jets-patriots",
                    "sport": "american football",
                    "league": "NFL",
                    "home": "Jets",
                    "away": "Patriots",
                    "event_date": now + timedelta(days=4),
                },
                {
                    "id": "nba-lakers-warriors",
                    "sport": "basketball",
                    "league": "NBA",
                    "home": "Lakers",
                    "away": "Warriors",
                    "event_date": now + timedelta(days=5),
                },
            ]
        }

    def _load_form_stub(self):
        return {
            "Arsenal": {"last_5": "WWDWW"},
            "Tottenham": {"last_5": "DLWDW"},
            "Jets": {"last_5": "LWLWL"},
            "Patriots": {"last_5": "LWLLL"},
            "Lakers": {"last_5": "WLWLW"},
            "Warriors": {"last_5": "WWLWW"},
        }

    def _load_injury_stub(self):
        return {
            "Arsenal": ["Starting LB doubtful"],
            "Jets": ["QB limited"],
            "Patriots": [],
            "Warriors": ["Wing out"],
        }

    def _load_weather_stub(self):
        return {
            "nfl-jets-patriots": {"forecast": "Windy", "impact": "moderate"},
            "soccer-arsenal-spurs": {"forecast": "Clear", "impact": "low"},
        }
