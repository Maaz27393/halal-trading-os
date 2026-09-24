import uuid
from typing import List
from predictive_risk.contracts.predictive_risk_contract import PredictiveRiskIndicator

class PredictiveRiskDetector:
    """
    Synthesizes multi-domain signals into forward-looking risk indicators
    and early-warning alerts across configurable horizons.
    """
    def evaluate_risk(self, category: str, domain: str, indicators: List[str], patterns: List[str], horizon: str, convergence_count: int) -> PredictiveRiskIndicator:
        level = "LOW_RISK"
        if convergence_count >= 4:
            level = "CRITICAL"
        elif convergence_count == 3:
            level = "HIGH_RISK"
        elif convergence_count == 2:
            level = "ELEVATED"
        elif convergence_count == 1:
            level = "WATCH"

        confidence = round(min(0.50 + (convergence_count * 0.12), 0.95), 2)

        return PredictiveRiskIndicator(
            risk_id=str(uuid.uuid4())[:8],
            risk_category=category,
            affected_domain=domain,
            risk_level=level,
            horizon=horizon,
            observed_indicators=indicators,
            historical_patterns=patterns,
            confidence_score=confidence
        )
