from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from ..config import get_logger
from ..models.prediction import ConfidenceTier, Prediction, PredictionSourceMix

logger = get_logger(__name__)


@dataclass
class PredictionInputs:
    fixture: Dict[str, str]
    form: Dict[str, Dict[str, str]]
    injuries: Dict[str, List[str]]
    weather: Dict[str, Dict[str, str]]
    analyst_mix: Dict[str, float]


def _confidence_from_probability(probability: float) -> ConfidenceTier:
    if probability >= 70:
        return ConfidenceTier.high
    if probability >= 55:
        return ConfidenceTier.medium
    return ConfidenceTier.low


def _source_mix(analyst: float, model: float, context: float) -> PredictionSourceMix:
    total = analyst + model + context
    if total == 0:
        return PredictionSourceMix(analyst=0, model=1, context=0)
    return PredictionSourceMix(
        analyst=analyst / total,
        model=model / total,
        context=context / total,
    )


class PredictionEngine:
    """Combines internal signals with analyst aggregation to emit probabilities."""

    def __init__(self, base_model_weight: float = 0.6, analyst_weight: float = 0.3, context_weight: float = 0.1):
        self.base_model_weight = base_model_weight
        self.analyst_weight = analyst_weight
        self.context_weight = context_weight

    def predict(self, inputs: PredictionInputs) -> List[Prediction]:
        fixture = inputs.fixture
        home, away = fixture["home"], fixture["away"]
        event_id = fixture["id"]
        event_date = fixture["event_date"]
        sport = fixture["sport"]
        league = fixture["league"]

        base_moneyline = self._base_probability_from_form(inputs.form.get(home), inputs.form.get(away))
        injury_adjustment = self._injury_adjustment(inputs.injuries, home, away)
        weather_adjustment = self._weather_adjustment(inputs.weather.get(event_id))
        analyst_view = inputs.analyst_mix.get("moneyline", 0.5)

        blended = (
            base_moneyline * self.base_model_weight
            + analyst_view * self.analyst_weight
            + weather_adjustment * self.context_weight
        )
        home_prob = min(max(blended + injury_adjustment, 0), 1)

        predictions: List[Prediction] = [
            Prediction(
                id=f"{event_id}-moneyline-home",
                sport=sport,
                league=league,
                event=f"{home} vs {away}",
                event_date=event_date,
                market_type="moneyline",
                prediction=f"{home} to win",
                probability=round(home_prob * 100, 1),
                confidence_tier=_confidence_from_probability(home_prob * 100),
                source_mix=_source_mix(self.analyst_weight, self.base_model_weight, self.context_weight),
                factors=self._explain(home, away, injury_adjustment, weather_adjustment),
            ),
            Prediction(
                id=f"{event_id}-moneyline-away",
                sport=sport,
                league=league,
                event=f"{home} vs {away}",
                event_date=event_date,
                market_type="moneyline",
                prediction=f"{away} to win",
                probability=round((1 - home_prob) * 100, 1),
                confidence_tier=_confidence_from_probability((1 - home_prob) * 100),
                source_mix=_source_mix(self.analyst_weight, self.base_model_weight, self.context_weight),
                factors=self._explain(away, home, -injury_adjustment, weather_adjustment),
            ),
        ]

        predictions.extend(self._build_prop_predictions(event_id, sport, league, fixture, event_date, inputs))
        logger.info("Generated %d predictions for event %s", len(predictions), event_id)
        return predictions

    def _base_probability_from_form(self, home_form: Dict[str, str] | None, away_form: Dict[str, str] | None) -> float:
        def form_score(form: Dict[str, str] | None) -> float:
            if not form:
                return 0.5
            mapping = {"W": 1, "D": 0.5, "L": 0}
            results = [mapping.get(char, 0.5) for char in form.get("last_5", "" )]
            return sum(results) / max(len(results), 1)

        home_score = form_score(home_form)
        away_score = form_score(away_form)
        total = home_score + away_score
        if total == 0:
            return 0.5
        return home_score / total

    def _injury_adjustment(self, injuries: Dict[str, List[str]], home: str, away: str) -> float:
        home_injuries = len(injuries.get(home, []))
        away_injuries = len(injuries.get(away, []))
        adjustment = (away_injuries - home_injuries) * 0.02
        return adjustment

    def _weather_adjustment(self, weather: Dict[str, str] | None) -> float:
        if not weather:
            return 0.5
        impact = weather.get("impact", "low")
        return {"low": 0.55, "moderate": 0.5, "high": 0.45}.get(impact, 0.5)

    def _build_prop_predictions(self, event_id: str, sport: str, league: str, fixture: Dict[str, str], event_date: datetime, inputs: PredictionInputs) -> List[Prediction]:
        home = fixture["home"]
        away = fixture["away"]
        prop_templates = [
            ("player prop", f"{home} key player over benchmark", 0.62),
            ("team prop", f"{away} over 2.5 team-specific metric", 0.48),
            ("event prop", f"{home} to record early momentum", 0.56),
        ]
        predictions: List[Prediction] = []
        for idx, (market_type, statement, base_prob) in enumerate(prop_templates):
            analyst_prob = inputs.analyst_mix.get(market_type, base_prob)
            blended_prob = (
                base_prob * self.base_model_weight
                + analyst_prob * self.analyst_weight
                + 0.5 * self.context_weight
            )
            predictions.append(
                Prediction(
                    id=f"{event_id}-{market_type}-{idx}",
                    sport=sport,
                    league=league,
                    event=f"{home} vs {away}",
                    event_date=event_date,
                    market_type=market_type,
                    prediction=statement,
                    probability=round(blended_prob * 100, 1),
                    confidence_tier=_confidence_from_probability(blended_prob * 100),
                    source_mix=_source_mix(self.analyst_weight, self.base_model_weight, self.context_weight),
                    factors=self._explain(home, away, 0, 0),
                )
            )
        return predictions

    def _explain(self, primary: str, opponent: str, injury_adjustment: float, weather_adjustment: float) -> List[str]:
        reasons = [
            f"Form favors {primary}",
            f"Opponent: {opponent}",
        ]
        if injury_adjustment:
            direction = "healthier" if injury_adjustment > 0 else "more injuries"
            reasons.append(f"Injury tilt: {direction}")
        if weather_adjustment != 0.5:
            reasons.append("Weather impact considered")
        return reasons
