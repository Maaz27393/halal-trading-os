from typing import Optional, Tuple
from datetime import datetime, timezone
from typing import Dict, Any, List
from data_quality.contracts.quality_contract import DataQualityMetadata, QualityState

class DataQualityValidator:
    """
    Evaluates incoming payloads against structural, freshness, and completeness criteria
    without modifying underlying provider or domain business logic.
    """
    def __init__(self, max_age_seconds: int = 300):
        self.max_age_seconds = max_age_seconds

    def validate_schema_and_completeness(self, payload: Dict[str, Any], required_fields: List[str]) -> Tuple[List[str], List[str]]:
        missing = []
        errors = []
        for field in required_fields:
            if field not in payload or payload[field] is None:
                missing.append(field)
                errors.append(f"Missing required field: {field}")
        return missing, errors

    def evaluate_freshness(self, source_timestamp: Optional[datetime]) -> QualityState:
        if source_timestamp is None:
            return QualityState.STALE
        
        now = datetime.now(timezone.utc)
        # Ensure timezone awareness for delta calculation
        if source_timestamp.tzinfo is None:
            source_timestamp = source_timestamp.replace(tzinfo=timezone.utc)
            
        age_seconds = (now - source_timestamp).total_seconds()
        
        if age_seconds < 0:
            return QualityState.INVALID
        elif age_seconds <= self.max_age_seconds:
            return QualityState.FRESH
        elif age_seconds <= self.max_age_seconds * 3:
            return QualityState.STALE
        else:
            return QualityState.EXPIRED
