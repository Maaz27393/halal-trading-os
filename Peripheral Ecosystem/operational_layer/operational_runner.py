import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Set

import pandas as pd

# ============================================================
# PROJECT PATH CONFIGURATION
# ============================================================

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = os.path.join(VAULT_ROOT, "Peripheral Ecosystem")
OPERATIONAL_DIR = os.path.join(ECOSYSTEM_DIR, "operational_layer")

if VAULT_ROOT not in sys.path:
    sys.path.insert(0, VAULT_ROOT)

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

if OPERATIONAL_DIR not in sys.path:
    sys.path.insert(0, OPERATIONAL_DIR)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("MultiModeOperationalRunner")


# ============================================================
# SECURITY INVARIANT
# ============================================================

LIVE_AUTO_EXECUTION = False


# ============================================================
# EXISTING PROJECT COMPONENTS
# ============================================================

from scanner_registry_loader import ScannerRegistryLoader
from chartink_operational_adapter import ChartinkOperationalAdapter


class MultiModeOperationalRunner:
    """
    M3.3 Registry-Governed Multi-Mode Operational Runner.

    Responsibilities:
        1. Load canonical 174-symbol Halal universe.
        2. Load and validate scanner registry.
        3. Select enabled PRE_MARKET scanners.
        4. Execute them through the existing Chartink operational adapter.
        5. Preserve scanner attribution.
        6. Calculate structural confluence.
        7. Export the resulting briefing to Obsidian.

    No live order execution is performed.
    """

    def __init__(
        self,
        vault_path: str = VAULT_ROOT
    ):
        self.vault_path = vault_path

        self.registry_path = os.path.join(
            self.vault_path,
            "Peripheral Ecosystem",
            "Canonical Universe",
            "scanner_registry.yaml"
        )

        self.halal_csv_path = os.path.join(
            self.vault_path,
            "Peripheral Ecosystem",
            "Canonical Universe",
            "canonical_halal_universe.csv"
        )

        # ----------------------------------------------------
        # Registry
        # ----------------------------------------------------

        self.registry_loader = ScannerRegistryLoader(
            self.registry_path
        )

        # ----------------------------------------------------
        # Mandatory canonical universe
        # ----------------------------------------------------

        self.canonical_halal_symbols = (
            self._load_canonical_universe()
        )

        if len(self.canonical_halal_symbols) == 0:
            raise RuntimeError(
                "CRITICAL: Canonical Halal universe resolved to "
                "0 symbols. Zero fallback permitted."
            )

        # ----------------------------------------------------
        # Registry-governed Chartink adapter
        # ----------------------------------------------------

        self.chartink_adapter = ChartinkOperationalAdapter(
            self.vault_path
        )

        logger.info(
            "M3.3 MultiModeOperationalRunner initialized."
        )

    # ========================================================
    # CANONICAL UNIVERSE
    # ========================================================

    def _load_canonical_universe(self) -> Set[str]:

        if not os.path.exists(self.halal_csv_path):
            raise RuntimeError(
                "CRITICAL: Mandatory canonical Halal universe "
                f"missing at:\n{self.halal_csv_path}"
            )

        df = pd.read_csv(self.halal_csv_path)

        symbol_col = next(
            (
                col
                for col in df.columns
                if col.lower() in [
                    "symbol",
                    "tradingsymbol"
                ]
            ),
            None
        )

        if not symbol_col:
            raise KeyError(
                "Canonical Halal CSV must contain either "
                "'symbol' or 'tradingsymbol'."
            )

        symbols = {
            str(symbol).upper().strip()
            for symbol in df[symbol_col].dropna()
            if str(symbol).strip()
        }

        logger.info(
            f"Loaded mandatory canonical Halal universe: "
            f"{len(symbols)} symbols."
        )

        return symbols

    # ========================================================
    # PRE-MARKET WORKFLOW
    # ========================================================

    def execute_pre_market_workflow(
        self,
        mock_connector_results: Dict[str, List[dict]] = None
    ) -> str:

        logger.info(
            "=================================================="
        )
        logger.info(
            "MODE: PRE_MARKET / STRUCTURAL"
        )
        logger.info(
            "=================================================="
        )

        if LIVE_AUTO_EXECUTION:
            raise RuntimeError(
                "SECURITY ERROR: "
                "LIVE_AUTO_EXECUTION must remain FALSE."
            )

        # ----------------------------------------------------
        # Select registry-governed scanners
        # ----------------------------------------------------

        pre_market_scanners = (
            self.registry_loader.get_scanners_by_mode(
                "PRE_MARKET"
            )
        )

        logger.info(
            f"Enabled PRE_MARKET scanners found: "
            f"{len(pre_market_scanners)}"
        )

        if not pre_market_scanners:
            raise RuntimeError(
                "CRITICAL: No enabled PRE_MARKET scanners "
                "were found in the scanner registry."
            )

        # ----------------------------------------------------
        # Confluence state
        # ----------------------------------------------------

        symbol_attributions: Dict[str, Set[str]] = {}
        symbol_metadata: Dict[str, dict] = {}

        scanner_results = []

        # ----------------------------------------------------
        # Execute each registered scanner
        # ----------------------------------------------------

        for scanner in pre_market_scanners:

            scanner_name = scanner["scanner_name"]
            slug = scanner["slug"]
            scanner_url = scanner["scanner_url"]

            label = scanner["attribution_label"]
            contributes = scanner[
                "contributes_to_confluence"
            ]

            requires_halal = scanner[
                "halal_intersection_required"
            ]

            logger.info(
                "--------------------------------------------------"
            )
            logger.info(
                f"Executing scanner: {scanner_name}"
            )
            logger.info(
                f"Slug: {slug}"
            )
            logger.info(
                f"URL: {scanner_url}"
            )

            # ------------------------------------------------
            # Mock path is retained strictly for regression
            # testing. Normal execution uses live adapter.
            # ------------------------------------------------

            if (
                mock_connector_results is not None
                and slug in mock_connector_results
            ):
                logger.info(
                    f"[{slug}] Using explicitly supplied "
                    "regression/mock data."
                )

                raw_records = mock_connector_results[slug]

                provenance = "MOCK_REGRESSION"

                meta_info = {
                    "raw_count": len(raw_records),
                    "parsed_count": len(raw_records),
                    "halal_match_count": len(raw_records),
                    "retained_count": len(raw_records)
                }

            else:

                raw_records = (
                    self.chartink_adapter.fetch_and_adapt_scan(
                        scanner_url,
                        self.canonical_halal_symbols
                    )
                )

                provenance = (
                    raw_records[0].get(
                        "provenance",
                        "LIVE_AUTHENTICATED"
                    )
                    if raw_records
                    else "LIVE_AUTHENTICATED"
                )

                meta_info = (
                    raw_records[0].get(
                        "meta_info",
                        {}
                    )
                    if raw_records
                    else {}
                )

            # ------------------------------------------------
            # Scanner reconciliation
            # ------------------------------------------------

            scanner_result = {
                "scanner_name": scanner_name,
                "slug": slug,
                "scanner_url": scanner_url,
                "provenance": provenance,
                "raw_count": meta_info.get(
                    "raw_count",
                    len(raw_records)
                ),
                "parsed_count": meta_info.get(
                    "parsed_count",
                    len(raw_records)
                ),
                "halal_match_count": meta_info.get(
                    "halal_match_count",
                    len(raw_records)
                ),
                "retained_count": meta_info.get(
                    "retained_count",
                    len(raw_records)
                )
            }

            scanner_results.append(scanner_result)

            logger.info(
                f"[{scanner_name}] "
                f"Raw={scanner_result['raw_count']} | "
                f"Parsed={scanner_result['parsed_count']} | "
                f"Halal={scanner_result['halal_match_count']} | "
                f"Retained={scanner_result['retained_count']} | "
                f"Provenance={provenance}"
            )

            # ------------------------------------------------
            # Build confluence
            # ------------------------------------------------

            for record in raw_records:

                sym = str(
                    record.get("symbol", "")
                ).upper().strip()

                if not sym:
                    continue

                # Defense-in-depth Halal boundary.
                if (
                    requires_halal
                    and sym not in self.canonical_halal_symbols
                ):
                    continue

                if sym not in symbol_attributions:

                    symbol_attributions[sym] = set()

                    symbol_metadata[sym] = {
                        "company": record.get(
                            "company",
                            sym
                        ),
                        "close": record.get(
                            "close",
                            0.0
                        ),
                        "volume": record.get(
                            "volume",
                            0
                        ),
                        "pct_change": record.get(
                            "pct_change",
                            0.0
                        ),
                        "provenance": record.get(
                            "provenance",
                            provenance
                        )
                    }

                if contributes:
                    symbol_attributions[sym].add(
                        label
                    )

        # ====================================================
        # CONFLUENCE RANKING
        # ====================================================

        ranked_candidates = []

        for sym, triggers in symbol_attributions.items():

            score = len(triggers)

            if score <= 0:
                continue

            meta = symbol_metadata[sym]

            ranked_candidates.append(
                {
                    "symbol": sym,
                    "company": meta["company"],
                    "close": meta["close"],
                    "volume": meta["volume"],
                    "pct_change": meta["pct_change"],
                    "score": score,
                    "triggers": sorted(triggers),
                    "provenance": meta["provenance"]
                }
            )

        ranked_candidates.sort(
            key=lambda x: (
                x["score"],
                x["volume"]
            ),
            reverse=True
        )

        logger.info(
            "=================================================="
        )
        logger.info(
            f"Structural candidates retained: "
            f"{len(ranked_candidates)}"
        )
        logger.info(
            "=================================================="
        )

        # ====================================================
        # EXPORT
        # ====================================================

        briefing_path = self._export_briefing(
            ranked_candidates,
            scanner_results
        )

        logger.info(
            f"Pre-market briefing exported: "
            f"{briefing_path}"
        )

        logger.info(
            "PRE_MARKET STRUCTURAL EXECUTION COMPLETED"
        )

        return briefing_path

    # ========================================================
    # BRIEFING EXPORT
    # ========================================================

    def _export_briefing(
        self,
        candidates: List[dict],
        scanner_results: List[dict]
    ) -> str:

        today_str = datetime.now().strftime(
            "%Y-%m-%d"
        )

        briefing_dir = os.path.join(
            self.vault_path,
            "Daily_Briefings"
        )

        os.makedirs(
            briefing_dir,
            exist_ok=True
        )

        briefing_file = os.path.join(
            briefing_dir,
            f"Briefing_{today_str}.md"
        )

        lines = [
            f"# Pre-Market Structural Briefing â€” "
            f"{today_str}",
            "",
            "> [!NOTE]",
            "> **DATA STATUS: "
            "M3.3 REGISTRY-GOVERNED STRUCTURAL SCANS**",
            f"> * **Active Mode:** "
            f"`PRE_MARKET / STRUCTURAL`",
            f"> * **Canonical Halal Universe:** "
            f"`{len(self.canonical_halal_symbols)} symbols`",
            f"> * **Scanners Executed:** "
            f"`{len(scanner_results)}`",
            "> * **Execution Boundary:** "
            "`LIVE_AUTO_EXECUTION = FALSE`",
            "",
            "---",
            "",
            "## Scanner Reconciliation",
            "",
            "| Scanner | Raw | Parsed | Halal | Retained | Provenance |",
            "|---|---:|---:|---:|---:|---|"
        ]

        for result in scanner_results:

            lines.append(
                f"| {result['scanner_name']} "
                f"| {result['raw_count']} "
                f"| {result['parsed_count']} "
                f"| {result['halal_match_count']} "
                f"| {result['retained_count']} "
                f"| `{result['provenance']}` |"
            )

        lines.extend(
            [
                "",
                "---",
                "",
                "## Structural Universe Confluence Ranking",
                "",
                "| Rank | Symbol | Company | Close (â‚¹) "
                "| Volume | % Chg | Score | Provenance "
                "| Scanners Triggered |",
                "|:---:|:---|:---|---:|---:|---:|---:|---|---|"
            ]
        )

        for idx, candidate in enumerate(
            candidates,
            1
        ):

            triggers = (
                "<br>â€¢ "
                + "<br>â€¢ ".join(
                    candidate["triggers"]
                )
            )

            lines.append(
                f"| {idx} "
                f"| **{candidate['symbol']}** "
                f"| {candidate['company']} "
                f"| {candidate['close']} "
                f"| {candidate['volume']:,} "
                f"| {candidate['pct_change']}% "
                f"| **{candidate['score']}** "
                f"| `{candidate['provenance']}` "
                f"| {triggers} |"
            )

        lines.extend(
            [
                "",
                "---",
                "",
                "## Recommended Next Stage",
                "",
                "1. Review the structural confluence ranking.",
                "2. Candidates may be placed into the "
                "**Breakout Confirmation Watchlist**.",
                "3. Perform human TradingView visual validation.",
                "4. During market hours, switch to "
                "**INTRADAY** confirmation scanners.",
                "",
                "> **Note:** This workflow does not modify "
                "Chartink watchlists automatically.",
                "> Watchlist modification remains outside "
                "this M3.3 execution path.",
                ""
            ]
        )

        with open(
            briefing_file,
            "w",
            encoding="utf-8"
        ) as f:
            f.write("\n".join(lines))

        return briefing_file


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    runner = MultiModeOperationalRunner()

    runner.execute_pre_market_workflow()
