import logging
from typing import Any, Dict, List, Set

from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver
from provider_connectors.step2_chartink_scanner import (
    ChartinkScannerConnector,
)

logger = logging.getLogger("ChartinkRegistryAdapter")


class ChartinkRegistryAdapter:
    """
    Registry-facing adapter for the production authenticated
    Chartink scanner connector.

    Architecture:

        CapabilityResolver
              |
              v
        ChartinkRegistryAdapter
              |
              v
        ChartinkScannerConnector
              |
              v
        Authenticated Chartink

    This adapter does not modify provider behavior, scanner
    queries, Halal filtering, or execution controls.
    """

    PROVIDER_ID = "chartink_authenticated"
    NAMESPACE = "technical.scanners"

    def __init__(self):
        self.provenance = ""
        self.last_meta_info: Dict[str, Any] = {}

    # ------------------------------------------------------------
    # REGISTRY CONTRACT
    # ------------------------------------------------------------

    def capabilities(self) -> List[str]:
        """
        Chartink is exposed to the registry as READ-only.
        """
        return ["READ"]

    def health(self) -> Dict[str, Any]:
        """
        Lightweight health declaration.

        Do not establish a live Chartink browser session here.
        Authentication is performed only during an actual scan.
        """
        return {
            "status": "healthy",
            "provider_id": self.PROVIDER_ID,
            "namespace": self.NAMESPACE,
            "capabilities": self.capabilities(),
            "read_only": True,
            "live_auto_execution": False,
            "execution_authority": "NONE",
        }

    # ------------------------------------------------------------
    # OPERATIONAL CONTRACT
    # ------------------------------------------------------------

    def fetch_and_adapt_scan(
        self,
        scanner_url: str,
        halal_symbols: Set[str],
    ) -> List[Dict[str, Any]]:
        """
        Delegate the actual authenticated scan to the existing
        production Chartink connector.

        The production connector remains authoritative for:
            - authentication
            - scanner metadata extraction
            - atlas_query execution
            - CSRF handling
            - Chartink response parsing
            - Halal intersection
            - LIVE_AUTO_EXECUTION safety block
        """

        logger.info(
            "Registry dispatch -> %s -> %s",
            self.PROVIDER_ID,
            scanner_url,
        )

        connector = ChartinkScannerConnector()

        try:
            connector.connect()

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
                if isinstance(meta_info, dict)
                else {}
            )

            if not isinstance(candidates, list):
                raise RuntimeError(
                    "Chartink connector returned an invalid "
                    "candidates object."
                )

            adapted_records: List[Dict[str, Any]] = []

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

                    "meta_info": self.last_meta_info,
                }

                adapted_records.append(record)

            logger.info(
                "Registry Chartink scan completed | "
                "Raw=%s | Parsed=%s | Halal=%s | Retained=%s",
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

        finally:
            connector.close()


def build_chartink_resolver() -> CapabilityResolver:
    """
    Build an isolated resolver containing the production
    authenticated Chartink provider.
    """

    resolver = CapabilityResolver()

    adapter = ChartinkRegistryAdapter()

    registration = ProviderRegistration(
        provider_id=adapter.PROVIDER_ID,
        namespace=adapter.NAMESPACE,
        adapter_instance=adapter,
        priority=10,
        enabled=True,
        health_status="healthy",
        supported_operations=["READ"],
        metadata={
            "provider_type": "authenticated_chartink",
            "read_only": True,
            "execution_authority": "NONE",
            "live_auto_execution": False,
        },
    )

    resolver.register_provider(registration)

    return resolver
