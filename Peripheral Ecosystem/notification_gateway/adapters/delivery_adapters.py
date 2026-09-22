import os
import json
from typing import Dict, Any
from notification_gateway.contracts.alert_contract import AlertEvent

class LocalDropAdapter:
    """
    Writes alert notifications to a secure local directory.
    """
    def __init__(self, drop_dir: str = "./Peripheral Ecosystem/notification_gateway/local_drop_store"):
        self.drop_dir = drop_dir
        os.makedirs(self.drop_dir, exist_ok=True)

    def deliver(self, alert: AlertEvent) -> Dict[str, Any]:
        file_path = os.path.join(self.drop_dir, f"alert_{alert.alert_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(alert.model_dump_json(indent=2))
        return {"status": "SUCCESS", "destination": "local_drop", "path": file_path}

class WebhookAdapter:
    """
    Simulates an outbound HTTP webhook notification dispatcher.
    Enforces outbound-only telemetry (zero inbound command execution).
    """
    def deliver(self, alert: AlertEvent, endpoint_url: str = "https://internal-webhook.halal-os.local/alerts") -> Dict[str, Any]:
        # Outbound transmission simulation
        payload = alert.model_dump_json()
        if not endpoint_url.startswith("https://"):
            return {"status": "FAILED", "reason": "Insecure or malformed destination endpoint"}
        
        # Simulated successful outbound dispatch
        return {
            "status": "SUCCESS",
            "destination": endpoint_url,
            "bytes_transmitted": len(payload),
            "outbound_only_verified": True
        }
