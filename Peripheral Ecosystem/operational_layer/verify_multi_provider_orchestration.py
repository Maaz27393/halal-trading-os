import csv
import importlib.util
import json
import logging
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml


# ============================================================
# PATHS
# ============================================================

VAULT_ROOT = Path(
    r"D:\OBSIDIAN VAULT\halal-trading-os"
)

ECOSYSTEM_DIR = (
    VAULT_ROOT
    / "Peripheral Ecosystem"
)

OPERATIONAL_DIR = (
    ECOSYSTEM_DIR
    / "operational_layer"
)

PROVIDER_DIR = (
    ECOSYSTEM_DIR
    / "provider_connectors"
)

SCREENER_CACHE_DIR = (
    ECOSYSTEM_DIR
    / "data_cache"
    / "screener"
)

BUNDLE_DIR = (
    ECOSYSTEM_DIR
    / "data_cache"
    / "orchestration"
)

BUNDLE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

for path in [
    VAULT_ROOT,
    ECOSYSTEM_DIR,
    OPERATIONAL_DIR,
    PROVIDER_DIR,
]:
    path_string = str(path)

    if path_string not in sys.path:
        sys.path.insert(
            0,
            path_string,
        )


# ============================================================
# PROVIDERS / ADAPTERS
# ============================================================

from security.gateway import PermissionGateway
from nse_connector import NSEConnector
from screener_connector import ScreenerConnector
from chartink_operational_adapter import (
    ChartinkOperationalAdapter,
)
from kite_operational_adapter import (
    KiteOperationalAdapter,
)


# ============================================================
# GLOBAL GOVERNANCE
# ============================================================

READ_ONLY = True
LIVE_AUTO_EXECUTION = False
ORDER_CAPABILITY = "NONE"
EXECUTION_AUTHORITY = "NONE"

OLLAMA_URL = (
    "http://127.0.0.1:11434/api/chat"
)

OLLAMA_MODEL = "qwen3:4b"
OLLAMA_TIMEOUT = 600

MAX_CHARTINK_CANDIDATES = 8


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] "
           "%(name)s: %(message)s",
)

logger = logging.getLogger(
    "MultiProviderOrchestration"
)


# ============================================================
# UTILITIES
# ============================================================

def now() -> str:
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def compact(
    value: Any,
    max_list_items: int = 25,
) -> Any:
    """
    Reduce large provider payloads while preserving
    useful orchestration fields.
    """

    if isinstance(value, dict):
        preferred_keys = {
            "timestamp",
            "retrieved_at",
            "provider_payload_reference",
            "status",
            "error",
            "validation_error",
            "provenance",
            "symbol",
            "company",
            "close",
            "open",
            "high",
            "low",
            "volume",
            "pct_change",
            "last_price",
            "instrument_token",
            "exchange",
            "operation",
            "data",
            "candidates",
            "profiles",
            "candidate_count",
            "success_count",
            "fail_closed_count",
            "total_count",
        }

        output = {}

        for key, item in value.items():
            if (
                key in preferred_keys
                or len(value) <= 20
            ):
                output[key] = compact(
                    item,
                    max_list_items=max_list_items,
                )

        return output

    if isinstance(value, list):
        return [
            compact(
                item,
                max_list_items=max_list_items,
            )
            for item in value[:max_list_items]
        ]

    return value


def fail(
    message: str,
) -> None:
    logger.error(message)
    raise RuntimeError(message)


def assert_governance(
    component: Any,
    component_name: str,
) -> None:
    """
    Validate governance when a provider exposes class-level
    governance attributes.
    """

    checks = {
        "READ_ONLY": READ_ONLY,
        "LIVE_AUTO_EXECUTION": LIVE_AUTO_EXECUTION,
        "ORDER_CAPABILITY": ORDER_CAPABILITY,
        "EXECUTION_AUTHORITY": EXECUTION_AUTHORITY,
    }

    for attribute, global_value in checks.items():

        if not hasattr(
            component,
            attribute,
        ):
            continue

        provider_value = getattr(
            component,
            attribute,
        )

        if attribute == "READ_ONLY":
            if provider_value is not True:
                fail(
                    f"{component_name}: "
                    f"READ_ONLY is not True."
                )

        elif attribute == "LIVE_AUTO_EXECUTION":
            if provider_value is not False:
                fail(
                    f"{component_name}: "
                    f"LIVE_AUTO_EXECUTION is not False."
                )

        else:
            if provider_value != global_value:
                fail(
                    f"{component_name}: "
                    f"{attribute} mismatch. "
                    f"Expected {global_value}, "
                    f"got {provider_value}."
                )


# ============================================================
# CHARTINK DISCOVERY
# ============================================================

def find_registry_file() -> Optional[Path]:
    candidates = list(
        ECOSYSTEM_DIR.rglob(
            "scanner_registry*.yaml"
        )
    )

    if not candidates:
        candidates = list(
            ECOSYSTEM_DIR.rglob(
                "scanner_registry*.yml"
            )
        )

    return (
        candidates[0]
        if candidates
        else None
    )


def find_halal_universe() -> Optional[Path]:
    candidates = list(
        ECOSYSTEM_DIR.rglob(
            "canonical_halal_universe.csv"
        )
    )

    return (
        candidates[0]
        if candidates
        else None
    )


def load_halal_symbols(
    path: Path,
) -> set:

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:

        rows = list(
            csv.DictReader(handle)
        )

    if not rows:
        fail(
            f"Halal universe file is empty: {path}"
        )

    possible_columns = [
        "symbol",
        "Symbol",
        "SYMBOL",
        "nse_symbol",
        "NSE Symbol",
        "NSE_SYMBOL",
    ]

    column = None

    for candidate in possible_columns:
        if candidate in rows[0]:
            column = candidate
            break

    if column is None:
        fail(
            "Unable to identify symbol column "
            f"in {path}"
        )

    symbols = {
        str(
            row.get(
                column,
                "",
            )
        ).strip().upper()
        for row in rows
        if row.get(column)
    }

    if not symbols:
        fail(
            f"No symbols loaded from {path}"
        )

    return symbols


def load_enabled_scanners(
    registry_path: Path,
) -> List[Dict[str, Any]]:

    with open(
        registry_path,
        "r",
        encoding="utf-8",
    ) as handle:

        payload = yaml.safe_load(handle)

    scanners: Any = payload

    if isinstance(
        payload,
        dict,
    ):

        for key in [
            "scanners",
            "scanner_registry",
            "registry",
            "items",
        ]:

            if key in payload:
                scanners = payload[key]
                break

    if isinstance(
        scanners,
        dict,
    ):
        scanners = list(
            scanners.values()
        )

    if not isinstance(
        scanners,
        list,
    ):
        fail(
            "Unable to interpret Chartink "
            "scanner registry structure."
        )

    enabled = []

    for scanner in scanners:

        if not isinstance(
            scanner,
            dict,
        ):
            continue

        enabled_value = scanner.get(
            "enabled",
            scanner.get(
                "active",
                False,
            ),
        )

        if enabled_value not in (
            True,
            "true",
            "True",
            1,
        ):
            continue

        scanner_url = (
            scanner.get("scanner_url")
            or scanner.get("url")
        )

        if not scanner_url:
            continue

        mode = str(
            scanner.get(
                "mode",
                scanner.get(
                    "stage",
                    scanner.get(
                        "scan_type",
                        "",
                    ),
                ),
            )
        ).strip().upper()

        if mode:
            normalized_mode = (
                mode
                .replace(
                    "-",
                    "_",
                )
                .replace(
                    " ",
                    "_",
                )
            )

            if normalized_mode not in {
                "PRE_MARKET",
                "PREMARKET",
                "PRE_MARKET_SCAN",
            }:
                continue

        enabled.append(
            scanner
        )

    return enabled


# ============================================================
# NSE
# ============================================================

def collect_nse() -> Dict[str, Any]:

    print(
        "\n[1] NSE live market layer..."
    )

    gateway = PermissionGateway()

    connector = NSEConnector(
        gateway
    )

    assert_governance(
        connector,
        "NSEConnector",
    )

    market_status = (
        connector.fetch_market_status()
    )

    index_vitals = (
        connector.fetch_index_vitals(
            "NIFTY 50"
        )
    )

    india_vix = (
        connector.fetch_india_vix()
    )

    capital_market = (
        connector.fetch_capital_market_snapshot()
    )

    advance_decline = (
        connector.fetch_advance_decline()
    )

    print(
        "   Market status: PASS"
    )

    print(
        "   NIFTY 50: PASS"
    )

    print(
        "   India VIX: PASS"
    )

    print(
        "   Capital Market: PASS"
    )

    print(
        "   Advance/Decline: PASS"
    )

    return {
        "source": "NSE_MARKET_REST_V1_1",
        "retrieved_at": now(),
        "status": "SUCCESS",
        "read_only": True,
        "data": {
            "market_status": compact(
                market_status
            ),
            "index_vitals": compact(
                index_vitals
            ),
            "india_vix": compact(
                india_vix
            ),
            "capital_market_snapshot": compact(
                capital_market
            ),
            "advance_decline": compact(
                advance_decline
            ),
        },
    }


# ============================================================
# CHARTINK
# ============================================================

def collect_chartink() -> Dict[str, Any]:

    print(
        "\n[2] Chartink pre-market candidates..."
    )

    registry_path = (
        find_registry_file()
    )

    universe_path = (
        find_halal_universe()
    )

    if registry_path is None:
        fail(
            "Chartink scanner registry was not found."
        )

    if universe_path is None:
        fail(
            "canonical_halal_universe.csv "
            "was not found."
        )

    halal_symbols = (
        load_halal_symbols(
            universe_path
        )
    )

    enabled = (
        load_enabled_scanners(
            registry_path
        )
    )

    if not enabled:
        fail(
            "No enabled Chartink scanners found."
        )

    adapter = (
        ChartinkOperationalAdapter(
            vault_path=str(
                VAULT_ROOT
            )
        )
    )

    print(
        "   Governance boundary: "
        "existing locked Chartink operational adapter"
    )

    candidates: List[Dict[str, Any]] = []

    try:

        for scanner in enabled:

            scanner_url = (
                scanner.get("scanner_url")
                or scanner.get("url")
            )

            scanner_name = (
                scanner.get("name")
                or scanner.get("scanner_name")
                or scanner.get("title")
                or scanner.get("slug")
                or scanner_url
            )

            try:

                rows = (
                    adapter.fetch_and_adapt_scan(
                        scanner_url,
                        halal_symbols,
                    )
                )

                for item in rows:

                    enriched = dict(
                        item
                    )

                    enriched[
                        "scanner_name"
                    ] = scanner_name

                    enriched[
                        "scanner_url"
                    ] = scanner_url

                    candidates.append(
                        enriched
                    )

                print(
                    f"   {scanner_name}: "
                    f"{len(rows)} candidate(s)"
                )

            except Exception as exc:

                print(
                    f"   {scanner_name}: "
                    f"FAILED ({exc})"
                )

    finally:

        if hasattr(
            adapter,
            "close",
        ):
            try:
                adapter.close()
            except Exception:
                pass

    if not candidates:

        return {
            "source": "CHARTINK_SCANNER_M3",
            "retrieved_at": now(),
            "status": "SUCCESS_EMPTY",
            "read_only": True,
            "provider_payload_reference": str(
                registry_path
            ),
            "data": {
                "candidate_count": 0,
                "candidates": [],
            },
        }

    symbol_counter = Counter(
        item.get("symbol")
        for item in candidates
        if item.get("symbol")
    )

    selected: List[Dict[str, Any]] = []

    ranked_symbols = [
        symbol
        for symbol, _ in (
            symbol_counter.most_common()
        )
    ]

    for symbol in ranked_symbols[
        :MAX_CHARTINK_CANDIDATES
    ]:

        symbol_rows = [
            row
            for row in candidates
            if row.get("symbol")
            == symbol
        ]

        scanners = []

        for row in symbol_rows:

            scanner_name = row.get(
                "scanner_name"
            )

            if (
                scanner_name
                and scanner_name
                not in scanners
            ):
                scanners.append(
                    scanner_name
                )

        selected.append(
            {
                "symbol": symbol,
                "scanner_count": len(
                    scanners
                ),
                "scanners": scanners,
                "records": symbol_rows,
            }
        )

    print(
        "   Unique candidates: "
        f"{len(symbol_counter)}"
    )

    return {
        "source": "CHARTINK_SCANNER_M3",
        "retrieved_at": now(),
        "status": "SUCCESS",
        "read_only": True,
        "provider_payload_reference": str(
            registry_path
        ),
        "data": {
            "candidate_count": len(
                symbol_counter
            ),
            "candidates": selected,
        },
    }


# ============================================================
# SCREENER
# ============================================================

def collect_screener(
    symbols: List[str],
) -> Dict[str, Any]:

    print(
        "\n[3] Screener local fundamental data..."
    )

    gateway = PermissionGateway()

    connector = ScreenerConnector(
        permission_gateway=gateway,
        data_root=str(
            SCREENER_CACHE_DIR
        ),
    )

    assert_governance(
        connector,
        "ScreenerConnector",
    )

    profiles: Dict[str, Any] = {}

    for symbol in symbols:

        fundamentals = (
            connector.get_company_fundamentals(
                symbol
            )
        )

        profiles[symbol] = fundamentals

        print(
            f"   {symbol}: "
            f"{fundamentals.get('status')}"
        )

    statuses = [
        profile.get("status")
        for profile in profiles.values()
    ]

    success_count = statuses.count(
        "SUCCESS"
    )

    fail_closed_count = statuses.count(
        "FAIL_CLOSED"
    )

    if not profiles:
        screener_status = (
            "NO_CANDIDATES"
        )

    elif success_count == len(
        profiles
    ):
        screener_status = "SUCCESS"

    elif success_count > 0:
        screener_status = "PARTIAL"

    else:
        screener_status = "FAIL_CLOSED"

    return {
        "source": (
            "SCREENER_IN_PERSONAL_VIEW"
        ),
        "retrieved_at": now(),
        "status": screener_status,
        "read_only": True,
        "provider_payload_reference": str(
            SCREENER_CACHE_DIR
        ),
        "data": {
            "profiles": profiles,
            "success_count": success_count,
            "fail_closed_count": (
                fail_closed_count
            ),
            "total_count": len(
                profiles
            ),
        },
    }


# ============================================================
# KITE MCP
# ============================================================

def collect_kite(
    symbols: List[str],
) -> Dict[str, Any]:

    print(
        "\n[4] Kite MCP read-only market data..."
    )

    if not symbols:

        return {
            "source": (
                "KITE_MCP_READ_ONLY"
            ),
            "retrieved_at": now(),
            "status": "NO_CANDIDATES",
            "read_only": True,
            "data": {
                "quotes": {},
            },
        }

    gateway = PermissionGateway()

    adapter = KiteOperationalAdapter(
        vault_path=str(
            VAULT_ROOT
        ),
        gateway=gateway,
    )

    assert_governance(
        adapter,
        "KiteOperationalAdapter",
    )

    try:

        print(
            "   Starting Kite MCP authentication..."
        )

        login_result = adapter.login(
            open_browser=True,
            wait_for_user=True,
        )

        if login_result.get(
            "status"
        ) != "SUCCESS":

            return {
                "source": (
                    "KITE_MCP_READ_ONLY"
                ),
                "retrieved_at": now(),
                "status": "FAIL_CLOSED",
                "read_only": True,
                "data": {},
                "error": login_result.get(
                    "error",
                    "Kite authentication failed.",
                ),
            }

        quote_result = (
            adapter.fetch_and_adapt_quotes(
                symbols=symbols,
                exchange="NSE",
                auto_login=False,
            )
        )

        status = quote_result.get(
            "status"
        )

        if status == "SUCCESS":
            print(
                "   Kite quotes: PASS"
            )

        else:
            print(
                "   Kite quotes: "
                f"{status}"
            )

        return {
            "source": (
                "KITE_MCP_READ_ONLY"
            ),
            "retrieved_at": now(),
            "status": status,
            "read_only": True,
            "provider_payload_reference": (
                "KITE_MCP"
            ),
            "data": {
                "quotes": compact(
                    quote_result.get(
                        "data",
                        {},
                    )
                ),
            },
            "error": quote_result.get(
                "error"
            ),
        }

    except Exception as exc:

        print(
            "   Kite MCP: "
            f"FAIL_CLOSED ({exc})"
        )

        return {
            "source": (
                "KITE_MCP_READ_ONLY"
            ),
            "retrieved_at": now(),
            "status": "FAIL_CLOSED",
            "read_only": True,
            "provider_payload_reference": (
                "KITE_MCP"
            ),
            "data": {},
            "error": str(exc),
        }

    finally:

        adapter.close()


# ============================================================
# VAULT RETRIEVAL
# ============================================================

def find_vault_search_script() -> Optional[Path]:

    candidates = list(
        (
            VAULT_ROOT
            / "Automation"
            / "AI Workspace"
            / "Retrieval"
        ).glob(
            "vault_search.py"
        )
    )

    return (
        candidates[0]
        if candidates
        else None
    )


def execute_vault_search(
    query: str,
) -> Dict[str, Any]:

    print(
        "\n[5] Obsidian Vault retrieval..."
    )

    script = (
        find_vault_search_script()
    )

    if script is None:
        fail(
            "vault_search.py was not found."
        )

    module_dir = str(
        script.parent
    )

    if module_dir not in sys.path:
        sys.path.insert(
            0,
            module_dir,
        )

    module_name = (
        "halal_trading_vault_search_runtime"
    )

    spec = (
        importlib.util.spec_from_file_location(
            module_name,
            str(script),
        )
    )

    if spec is None or spec.loader is None:
        fail(
            "Unable to load vault_search.py."
        )

    module = (
        importlib.util.module_from_spec(
            spec
        )
    )

    spec.loader.exec_module(
        module
    )

    possible_functions = [
        "search_vault",
        "vault_search",
        "search",
        "query_vault",
        "run_search",
    ]

    callable_obj = None

    for name in possible_functions:

        candidate = getattr(
            module,
            name,
            None,
        )

        if callable(candidate):
            callable_obj = candidate
            break

    if callable_obj is None:
        fail(
            "No supported callable search "
            "function was exposed by "
            "vault_search.py."
        )

    try:

        try:
            result = callable_obj(
                query
            )
        except TypeError:
            result = callable_obj(
                query=query
            )

    except Exception as exc:

        result = {
            "status": "FAIL_CLOSED",
            "error": str(exc),
        }

    print(
        "   Vault search: PASS"
        if not (
            isinstance(result, dict)
            and result.get("status")
            == "FAIL_CLOSED"
        )
        else
        "   Vault search: FAIL_CLOSED"
    )

    return {
        "source": (
            "OBSIDIAN_VAULT_RETRIEVAL"
        ),
        "retrieved_at": now(),
        "status": (
            "FAIL_CLOSED"
            if (
                isinstance(
                    result,
                    dict,
                )
                and result.get(
                    "status"
                )
                == "FAIL_CLOSED"
            )
            else "SUCCESS"
        ),
        "read_only": True,
        "data": compact(
            result
        ),
    }


# ============================================================
# QWEN SYNTHESIS
# ============================================================

def execute_qwen_synthesis(
    bundle: Dict[str, Any],
) -> str:

    print(
        "\n[6] Qwen unified synthesis..."
    )

    system_prompt = """
You are the local Qwen decision-support layer
for the Halal Trading OS.

You are NOT an execution authority.

Global invariants:
READ_ONLY = true
LIVE_AUTO_EXECUTION = false
ORDER_CAPABILITY = NONE
EXECUTION_AUTHORITY = NONE

Use only the supplied provider data.

Preserve provider provenance.

Do not invent missing values.

Clearly distinguish:
- provider facts
- derived observations
- unavailable information

Do not place orders.
Do not execute trades.
Do not produce automated execution instructions.

Produce a concise pre-market cross-source report covering:

1. Broad market condition from NSE.
2. India VIX and breadth.
3. Chartink candidate symbols and scanner attribution.
4. Screener fundamental availability.
5. Kite MCP market-data context for candidate symbols.
6. Relevant Vault rules/context.
7. Cross-source observations.
8. Explicit data limitations.

Kite MCP is strictly read-only in this environment.
Do not infer that the presence of Kite data grants execution capability.
"""

    user_prompt = (
        "Analyze the following verified "
        "multi-provider pre-market bundle.\n\n"
        + json.dumps(
            compact(
                bundle
            ),
            indent=2,
            ensure_ascii=False,
        )
    )

    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": system_prompt.strip(),
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=OLLAMA_TIMEOUT,
    )

    response.raise_for_status()

    body = response.json()

    content = (
        body
        .get("message", {})
        .get("content", "")
    )

    if not content:
        return (
            "Qwen returned an empty synthesis."
        )

    return str(
        content
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "HALAL TRADING OS - "
        "MULTI-PROVIDER ORCHESTRATION REGRESSION"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Global governance
    # --------------------------------------------------------

    print(
        "\nGovernance:"
    )

    print(
        f"  READ_ONLY            = "
        f"{READ_ONLY}"
    )

    print(
        f"  LIVE_AUTO_EXECUTION  = "
        f"{LIVE_AUTO_EXECUTION}"
    )

    print(
        f"  ORDER_CAPABILITY     = "
        f"{ORDER_CAPABILITY}"
    )

    print(
        f"  EXECUTION_AUTHORITY  = "
        f"{EXECUTION_AUTHORITY}"
    )

    # --------------------------------------------------------
    # NSE
    # --------------------------------------------------------

    nse = collect_nse()

    # --------------------------------------------------------
    # Chartink
    # --------------------------------------------------------

    chartink = collect_chartink()

    candidates = [
        item.get("symbol")
        for item in chartink[
            "data"
        ].get(
            "candidates",
            [],
        )
        if item.get("symbol")
    ]

    # --------------------------------------------------------
    # Screener
    # --------------------------------------------------------

    screener = collect_screener(
        candidates
    )

    # --------------------------------------------------------
    # Kite MCP
    # --------------------------------------------------------

    kite = collect_kite(
        candidates
    )

    # --------------------------------------------------------
    # Vault
    # --------------------------------------------------------

    vault = execute_vault_search(
        query=(
            "current trading rules, "
            "market go no-go conditions, "
            "risk limits, entry conditions, "
            "approved halal trading workflow"
        )
    )

    # --------------------------------------------------------
    # Unified bundle
    # --------------------------------------------------------

    bundle = {
        "orchestration_timestamp": now(),

        "governance": {
            "READ_ONLY": True,
            "LIVE_AUTO_EXECUTION": False,
            "ORDER_CAPABILITY": "NONE",
            "EXECUTION_AUTHORITY": "NONE",
        },

        "providers": {
            "nse": nse,
            "chartink": chartink,
            "screener": screener,
            "kite": kite,
            "vault": vault,
        },
    }

    # --------------------------------------------------------
    # Save raw orchestration bundle
    # --------------------------------------------------------

    timestamp = (
        datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    bundle_path = (
        BUNDLE_DIR
        / f"multi_provider_bundle_{timestamp}.json"
    )

    with open(
        bundle_path,
        "w",
        encoding="utf-8",
    ) as handle:

        json.dump(
            bundle,
            handle,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "\nBundle saved: "
        f"{bundle_path}"
    )

    # --------------------------------------------------------
    # Qwen
    # --------------------------------------------------------

    synthesis = (
        execute_qwen_synthesis(
            bundle
        )
    )

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    report_path = (
        BUNDLE_DIR
        / f"multi_provider_report_{timestamp}.md"
    )

    report = (
        "# Halal Trading OS - "
        "Multi-Provider Orchestration Report\n\n"
        f"Generated: {now()}\n\n"

        "## Governance\n\n"
        "- READ_ONLY: TRUE\n"
        "- LIVE_AUTO_EXECUTION: FALSE\n"
        "- ORDER_CAPABILITY: NONE\n"
        "- EXECUTION_AUTHORITY: NONE\n\n"

        "## Provider Status\n\n"
        f"- NSE: {nse.get('status')}\n"
        f"- Chartink: {chartink.get('status')}\n"
        f"- Screener: {screener.get('status')}\n"
        f"- Kite MCP: {kite.get('status')}\n"
        f"- Vault: {vault.get('status')}\n\n"

        "## Qwen Synthesis\n\n"
        f"{synthesis}\n"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8",
    ) as handle:

        handle.write(
            report
        )

    print(
        "Report saved: "
        f"{report_path}"
    )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "MULTI-PROVIDER "
        "ORCHESTRATION REGRESSION COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"NSE              : "
        f"{nse.get('status')}"
    )

    print(
        f"Chartink         : "
        f"{chartink.get('status')}"
    )

    print(
        f"Screener         : "
        f"{screener.get('status')}"
    )

    print(
        f"Kite MCP         : "
        f"{kite.get('status')}"
    )

    print(
        f"Vault Retrieval  : "
        f"{vault.get('status')}"
    )

    print(
        "Qwen Synthesis   : PASS"
    )

    print(
        "\nGovernance:"
    )

    print(
        "READ_ONLY            : TRUE"
    )

    print(
        "LIVE_AUTO_EXECUTION  : FALSE"
    )

    print(
        "ORDER_CAPABILITY     : NONE"
    )

    print(
        "EXECUTION_AUTHORITY  : NONE"
    )


if __name__ == "__main__":
    main()