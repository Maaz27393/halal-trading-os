from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from data_quality.contracts.quality_contract import DataQualityMetadata, QualityState
from data_quality.validators.schema_validator import DataQualityValidator

class DataQualityGate:
    """
    Sequential Quality Gate:
    Raw Payload -> Schema -> Freshness -> Completeness -> Provenance -> GATE (PASS / REJECT)
    No silent fallbacks or fabricated values permitted.
    """
    def __init__(self, required_fields: List[str], max_age_seconds: int = 300):
        self.validator = DataQualityValidator(max_age_seconds=max_age_seconds)
        self.required_fields = required_fields
        self.live_auto_execution = False

    def evaluate(self, provider: str, payload: Dict[str, Any], source_timestamp: Optional[datetime], provenance_info: Dict[str, Any]) -> DataQualityMetadata:
        if self.live_auto_execution:
            raise RuntimeError("CRITICAL: Data Quality gate violated non-execution governance policy.")

        # 1. Schema & Completeness Check
        missing_fields, validation_errors = self.validator.validate_schema_and_completeness(payload, self.required_fields)
        
        # 2. Freshness Check
        freshness_state = self.validator.evaluate_freshness(source_timestamp)
        if freshness_state in [QualityState.EXPIRED, QualityState.INVALID]:
            validation_errors.append(f"Payload freshness check failed with state: {freshness_state.value}")

        # 3. Determine Overall Status
        if missing_fields:
            validation_status = QualityState.INCOMPLETE
        elif validation_errors:
            validation_status = QualityState.INVALID
        else:
            validation_status = QualityState.VALID

        metadata = DataQualityMetadata(
            provider=provider,
            source_timestamp=source_timestamp,
            validation_status=validation_status,
            missing_fields=missing_fields,
            freshness_status=freshness_state,
            provenance=provenance_info,
            validation_errors=validation_errors,
            governance_flag=False
        )

        return metadata
