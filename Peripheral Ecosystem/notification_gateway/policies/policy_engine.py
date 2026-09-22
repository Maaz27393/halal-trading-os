from typing import Dict, Any
from notification_gateway.contracts.alert_contract import AlertEvent

class AlertPolicyEngine:
    """
    Evaluates alert severity and determines delivery actions (e.g. archive only vs. webhook broadcast).
    Guarantees zero automated remediation.
    """
    def evaluate_policy(self, severity: str) -> Dict[str, Any]:
        sev = severity.upper()
        if sev == "INFO":
            return {"action": "ARCHIVE_ONLY", "channels": ["local_drop"]}
        elif sev == "WARNING":
            return {"action": "NOTIFY_AND_ARCHIVE", "channels": ["local_drop", "webhook"]}
        elif sev == "CRITICAL":
            return {"action": "URGENT_NOTIFY_AND_AUDIT", "channels": ["local_drop", "webhook"], "audit_required": True}
        else:
            return {"action": "DEFAULT_ARCHIVE", "channels": ["local_drop"]}
