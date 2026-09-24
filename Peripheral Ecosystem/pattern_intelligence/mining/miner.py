import uuid
from typing import List
from pattern_intelligence.contracts.pattern_contract import OperationalPattern

class PatternMiner:
    """
    Mines cross-domain historical evidence to detect recurring operational patterns
    and behavioral sequences across reliability, performance, and capacity domains.
    """
    def mine_pattern(self, domains: List[str], name: str, desc: str, occurrences: int, confidence: float, regime: str) -> OperationalPattern:
        return OperationalPattern(
            pattern_id=str(uuid.uuid4())[:8],
            source_domains=domains,
            pattern_name=name,
            description=desc,
            occurrence_count=occurrences,
            confidence_score=confidence,
            regime_state=regime
        )
