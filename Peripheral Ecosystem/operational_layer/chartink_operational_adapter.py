import logging
import os
import sys
from typing import List, Dict, Any

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"

for path in [
    VAULT_ROOT,
    ECOSYSTEM_DIR,
]:
    if path not in sys.path:
        sys.path.insert(0, path)

from operational_layer.chartink_registry_adapter import (
    build_chartink_resolver,
    ChartinkRegistryAdapter,
)


logger = logging.getLogger(
    "ChartinkOperationalAdapter"
)


class ChartinkOperationalAdapter:
    """
    Registry-governed operational adapter for Chartink.

    Contract:

        Operational Runner
            ->
        CapabilityResolver
            ->
        ChartinkRegistryAdapter
            ->
        Production ChartinkScannerConnector

    The public fetch_and_adapt_scan() contract is preserved so
    existing operational-runner behavior remains unchanged.
    """

    def __init__(
        self,
        vault_path: str = VAULT_ROOT,
    ):
        self.vault_path = vault_path

        self.resolver = build_chartink_resolver()

        self.provenance = ""
        self.last_meta_info: Dict[str, Any] = {}

    def fetch_and_adapt_scan(
        self,
        scanner_url: str,
        halal_symbols: set,
    ) -> List[Dict[str, Any]]:
        """
        Execute the registered authenticated Chartink provider
        and return the stable operational-layer contract.

        The provider remains responsible for:
            - authenticated session
            - exact saved scanner query
            - CSRF
            - Chartink request
            - Halal intersection
            - execution safety
        """

        logger.info(
            "Registry dispatch to Chartink: %s",
            scanner_url,
        )

        try:

            records = self.resolver.execute_via_capability(
                namespace=ChartinkRegistryAdapter.NAMESPACE,
                method_name="fetch_and_adapt_scan",
                required_operation="READ",
                scanner_url=scanner_url,
                halal_symbols=halal_symbols,
            )

            if not isinstance(records, list):
                raise RuntimeError(
                    "Chartink registry adapter returned an "
                    "invalid records object."
                )

            adapter = self.resolver.resolve_adapter(
                ChartinkRegistryAdapter.NAMESPACE
            )

            self.provenance = getattr(
                adapter,
                "provenance",
                "LIVE_AUTHENTICATED",
            )

            self.last_meta_info = getattr(
                adapter,
                "last_meta_info",
                {},
            )

            if not isinstance(
                self.last_meta_info,
                dict,
            ):
                self.last_meta_info = {}

            logger.info(
                "Chartink operational registry dispatch "
                "completed | Provider=%s | Raw=%s | "
                "Parsed=%s | Halal=%s | Retained=%s",
                ChartinkRegistryAdapter.PROVIDER_ID,
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
                    len(records),
                ),
            )

            return records

        except Exception as exc:

            logger.error(
                "Chartink registry adapter failure for %s: %s",
                scanner_url,
                exc,
            )

            raise RuntimeError(
                f"Chartink registry dispatch failure "
                f"for {scanner_url}: {exc}"
            ) from exc
