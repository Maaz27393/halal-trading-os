import logging
import os
import sys
from typing import List, Dict, Any

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"
PROVIDER_DIR = rf"{ECOSYSTEM_DIR}\provider_connectors"

for path in [
    VAULT_ROOT,
    ECOSYSTEM_DIR,
    PROVIDER_DIR,
]:
    if path not in sys.path:
        sys.path.insert(0, path)

from security.gateway import PermissionGateway
from provider_connectors.step2_chartink_scanner import (
    ChartinkScannerConnector,
)


logger = logging.getLogger(
    "ChartinkOperationalAdapter"
)


class ChartinkOperationalAdapter:
    """
    Operational adapter for the locked Chartink scanner connector.

    Contract:
        Connector
            ->
        TechnicalCandidate objects
            +
        provenance
            +
        meta_info
            ->
        List[Dict[str, Any]]

    The adapter does not alter scanner queries or provider logic.
    """

    def __init__(
        self,
        vault_path: str = VAULT_ROOT,
        gateway: PermissionGateway = None,
    ):
        self.vault_path = vault_path

        self.gateway = (
            gateway
            if gateway is not None
            else PermissionGateway()
        )

        self.provenance = ""
        self.last_meta_info: Dict[str, Any] = {}

    def fetch_and_adapt_scan(
        self,
        scanner_url: str,
        halal_symbols: set,
    ) -> List[Dict[str, Any]]:
        """
        Execute a live Chartink scan and return the stable
        operational-layer contract expected by operational_runner.py.

        Return format:

        [
            {
                "symbol": "...",
                "company": "...",
                "close": 0.0,
                "volume": 0,
                "pct_change": 0.0,
                "provenance": "...",
                "meta_info": {...}
            }
        ]
        """

        logger.info(
            "Adapter connecting to Chartink scanner: %s",
            scanner_url,
        )

        try:

            with ChartinkScannerConnector(
                self.gateway
            ) as connector:

                (
                    candidates,
                    provenance,
                    meta_info,
                ) = connector.run_saved_scan(
                    halal_symbols,
                    scanner_url,
                )

                self.provenance = provenance
                self.last_meta_info = (
                    meta_info
                    if isinstance(
                        meta_info,
                        dict,
                    )
                    else {}
                )

                if not isinstance(
                    candidates,
                    list,
                ):
                    raise RuntimeError(
                        "Chartink connector returned an "
                        "invalid candidates object."
                    )

                adapted_records: List[
                    Dict[str, Any]
                ] = []

                for candidate in candidates:

                    record = {
                        "symbol": str(
                            getattr(
                                candidate,
                                "symbol",
                                "",
                            )
                        ).upper().strip(),

                        "company": str(
                            getattr(
                                candidate,
                                "company_name",
                                "",
                            )
                        ),

                        "close": float(
                            getattr(
                                candidate,
                                "close_price",
                                0.0,
                            )
                        ),

                        "volume": int(
                            getattr(
                                candidate,
                                "volume",
                                0,
                            )
                        ),

                        "pct_change": float(
                            getattr(
                                candidate,
                                "per_change",
                                0.0,
                            )
                        ),

                        "provenance": provenance,

                        "meta_info": (
                            self.last_meta_info
                        ),
                    }

                    adapted_records.append(
                        record
                    )

                logger.info(
                    "Chartink scan completed "
                    "[Provenance: %s] | "
                    "Raw: %s | "
                    "Parsed: %s | "
                    "Halal Matched: %s | "
                    "Retained: %s",
                    provenance,
                    self.last_meta_info.get(
                        "raw_count",
                        "N/A",
                    ),
                    self.last_meta_info.get(
                        "parsed_count",
                        "N/A",
                    ),
                    self.last_meta_info.get(
                        "halal_match_count",
                        "N/A",
                    ),
                    self.last_meta_info.get(
                        "retained_count",
                        len(adapted_records),
                    ),
                )

                return adapted_records

        except Exception as exc:

            logger.error(
                "Chartink adapter failure for %s: %s",
                scanner_url,
                exc,
            )

            raise RuntimeError(
                f"Connector failure for "
                f"{scanner_url}: {exc}"
            ) from exc