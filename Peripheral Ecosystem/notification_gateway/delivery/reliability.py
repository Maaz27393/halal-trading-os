import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from notification_gateway.contracts.alert_contract import AlertEvent
from notification_gateway.adapters.delivery_adapters import LocalDropAdapter, WebhookAdapter

class DeliveryTelemetryManager:
    """
    Manages delivery lifecycle (QUEUED -> DELIVERING -> DELIVERED / FAILED),
    retries, dead-lettering, and duplicate suppression.
    """
    def __init__(self):
        self.local_adapter = LocalDropAdapter()
        self.webhook_adapter = WebhookAdapter()
        self.delivered_cache = set()
        self.audit_telemetry = []

    def process_alert(self, alert: AlertEvent, webhook_url: str = "https://internal-webhook.halal-os.local/alerts") -> Dict[str, Any]:
        # Duplicate suppression check
        if alert.alert_id in self.delivered_cache:
            return {"alert_id": alert.alert_id, "status": "DUPLICATE_SUPPRESSED"}
        
        self.delivered_cache.add(alert.alert_id)
        
        results = {}
        channels = alert.delivery_policy.get("channels", ["local_drop"])

        # Lifecycle: QUEUED -> DELIVERING
        for channel in channels:
            attempt = 1
            max_retries = 3
            success = False
            last_err = None

            while attempt <= max_retries and not success:
                try:
                    if channel == "local_drop":
                        res = self.local_adapter.deliver(alert)
                        if res.get("status") == "SUCCESS":
                            success = True
                            results[channel] = res
                    elif channel == "webhook":
                        res = self.webhook_adapter.deliver(alert, webhook_url)
                        if res.get("status") == "SUCCESS":
                            success = True
                            results[channel] = res
                        else:
                            raise Exception(res.get("reason", "Webhook delivery failed"))
                except Exception as e:
                    last_err = str(e)
                    attempt += 1

            if not success:
                # Dead-letter fallback
                results[channel] = {"status": "DEAD_LETTER", "error": last_err, "attempts": max_retries}

        telemetry_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alert_id": alert.alert_id,
            "investigation_id": alert.investigation_id,
            "lifecycle_results": results,
            "safety_invariant": "OUTBOUND_ONLY_NO_EXECUTION"
        }
        self.audit_telemetry.append(telemetry_record)
        return telemetry_record
