from __future__ import annotations

import json
import requests
from datetime import datetime, timezone

CDP_VERSION_URL = "http://127.0.0.1:9222/json/version"
CDP_LIST_URL = "http://127.0.0.1:9222/json"

def fetch_cdp_telemetry() -> dict:
    """
    Queries the local TradingView Desktop Chrome DevTools Protocol (CDP) 
    endpoint in a strictly read-only fashion to capture active target metadata.
    """
    print("=" * 72)
    print("TRADINGVIEW CDP TELEMETRY BRIDGE - READ-ONLY PROBE")
    print("=" * 72)

    try:
        version_res = requests.get(CDP_VERSION_URL, timeout=3)
        version_data = version_res.json()

        list_res = requests.get(CDP_LIST_URL, timeout=3)
        targets = list_res.json()

        # Isolate the active chart page target
        chart_target = next((t for t in targets if "tradingview.com/chart" in t.get("url", "")), None)

        telemetry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "governance": {
                "read_only": True,
                "order_capability": "NONE",
                "execution_authority": "NONE"
            },
            "cdp_connection": {
                "browser": version_data.get("Browser"),
                "protocol_version": version_data.get("Protocol-Version"),
                "connected": True
            },
            "active_chart": {
                "title": chart_target.get("title") if chart_target else "Unknown Chart",
                "url": chart_target.get("url") if chart_target else "No active chart URL found",
                "target_id": chart_target.get("id") if chart_target else None
            }
        }

        print("[SUCCESS] Read-only CDP telemetry captured successfully:")
        print(json.dumps(telemetry, indent=2))
        return telemetry

    except Exception as e:
        error_payload = {
            "status": "FAIL_CLOSED",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        print(f"\n[FAIL_CLOSED] Could not connect to CDP endpoint: {e}")
        return error_payload

if __name__ == "__main__":
    fetch_cdp_telemetry()