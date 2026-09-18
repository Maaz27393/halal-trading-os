import os
import yaml
import logging

logger = logging.getLogger("ScannerRegistryLoader")

class ScannerRegistryLoader:
    SCHEMA_FIELDS = {
        "scanner_id": str,
        "scanner_name": str,
        "slug": str,
        "scanner_url": str,
        "enabled": bool,
        "operational_mode": list,
        "role": list,
        "input_watchlist": list,
        "halal_intersection_required": bool,
        "contributes_to_confluence": bool,
        "output_purpose": list,
        "priority": int,
        "minimum_confluence_contribution": int,
        "attribution_label": str,
        "notes": str
    }

    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self.scanners = self._load_and_validate()

    def _load_and_validate(self) -> list[dict]:
        if not os.path.exists(self.registry_path):
            raise FileNotFoundError(f"Mandatory scanner registry missing: {self.registry_path}")
        
        with open(self.registry_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        scanners = data.get("scanners", [])
        validated_scanners = []

        for idx, scn in enumerate(scanners):
            for field, expected_type in self.SCHEMA_FIELDS.items():
                if field not in scn:
                    raise ValueError(f"Scanner entry #{idx} missing mandatory schema field: '{field}'")
                if not isinstance(scn[field], expected_type):
                    raise TypeError(f"Scanner '{scn.get('scanner_id', idx)}' field '{field}' must be of type {expected_type.__name__}")
            validated_scanners.append(scn)

        logger.info(f"Successfully loaded and validated {len(validated_scanners)} scanners from registry.")
        return validated_scanners

    def get_scanners_by_mode(self, mode: str) -> list[dict]:
        return [s for s in self.scanners if s["enabled"] and mode in s["operational_mode"]]