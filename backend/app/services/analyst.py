from __future__ import annotations

from typing import Dict, List

from ..config import get_logger
from ..models.prediction import AnalystSignal

logger = get_logger(__name__)


class AnalystAggregator:
    """Normalizes and weights public analyst views into a single signal."""

    def __init__(self, baseline_credibility: float = 0.6):
        self.baseline_credibility = baseline_credibility

    def aggregate(self, signals: List[AnalystSignal]) -> Dict[str, float]:
        weighted: Dict[str, float] = {}
        total_weight = 0.0
        for signal in signals:
            weight = max(signal.credibility, self.baseline_credibility)
            total_weight += weight
            for market, prob in signal.market_view.items():
                weighted[market] = weighted.get(market, 0) + prob * weight
            logger.debug("Analyst %s applied with weight %.2f", signal.analyst, weight)
        if total_weight == 0:
            return {}
        normalized = {market: prob / total_weight for market, prob in weighted.items()}
        logger.info("Aggregated analyst signals across %d inputs", len(signals))
        return normalized
