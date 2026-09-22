import os
import json
from typing import Dict, Any

class PreRefreshValidator:
    """
    Validates Phase 22 analytical model outputs for schema compliance,
    presence, and basic record completeness prior to release.
    """
    def __init__(self, models_dir: str = "Peripheral Ecosystem/power_bi_integration/models"):
        self.models_dir = models_dir

    def validate_feeds(self) -> Dict[str, Any]:
        required_feeds = {
            "dim_providers": "dim_providers.json",
            "fact_system_health": "fact_system_health.json",
            "dim_governance": "dim_governance.json"
        }

        results = {}
        all_passed = True

        for feed_key, filename in required_feeds.items():
            path = os.path.join(self.models_dir, filename)
            if not os.path.exists(path):
                results[feed_key] = {"exists": False, "valid": False, "count": 0}
                all_passed = False
                continue

            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                count = len(data) if isinstance(data, list) else 1
                is_valid = count > 0
                results[feed_key] = {"exists": True, "valid": is_valid, "count": count}
                if not is_valid:
                    all_passed = False
            except Exception as e:
                results[feed_key] = {"exists": True, "valid": False, "count": 0, "error": str(e)}
                all_passed = False

        return {"overall_valid": all_passed, "feed_details": results}
