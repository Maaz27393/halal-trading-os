from datetime import datetime, timezone
from typing import Dict, Any

class InvestigationAuditLogger:
    """
    Records immutable audit entries for all investigation runs.
    """
    def __init__(self):
        self.audit_log = []

    def record_audit(self, investigation_id: str, trigger: str, status: str) -> Dict[str, Any]:
        record = {
            "audit_timestamp": datetime.now(timezone.utc).isoformat(),
            "investigation_id": investigation_id,
            "trigger": trigger,
            "status": status,
            "safety_guard": "STRICTLY_READ_ONLY_EVIDENCE"
        }
        self.audit_log.append(record)
        return record
