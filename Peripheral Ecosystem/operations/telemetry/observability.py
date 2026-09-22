import logging
from typing import Dict, Any
from operations.contracts.operational_contract import OperationalEvent

logger = logging.getLogger("UnifiedTelemetry")

class SystemObservabilityAggregator:
    """
    Collects and aggregates unified operational telemetry across all domains,
    ensuring continuous observability without breaking governance boundaries.
    """
    def __init__(self):
        self.live_auto_execution = False
        self.domain_healths: Dict[str, str] = {}
        logger.info("SystemObservabilityAggregator initialized (Read-Only / Ops Mode).")

    def record_domain_status(self, domain: str, status: str) -> None:
        if self.live_auto_execution:
            raise RuntimeError("CRITICAL: Operations layer violated non-execution policy.")
        self.domain_healths[domain] = status

    def get_system_health_summary(self) -> Dict[str, Any]:
        return {
            "live_auto_execution": self.live_auto_execution,
            "domains": self.domain_healths,
            "overall_status": "HEALTHY" if all(s == "HEALTHY" for s in self.domain_healths.values()) else "DEGRADED"
        }
