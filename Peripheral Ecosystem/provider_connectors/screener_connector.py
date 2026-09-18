import csv
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"

if VAULT_ROOT not in sys.path:
    sys.path.insert(0, VAULT_ROOT)

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

from security.gateway import PermissionGateway


class ScreenerConnector:
    """
    Read-only Screener.in personal-data ingestion connector.

    IMPORTANT:
        This connector does NOT scrape Screener.in.
        It consumes authorized local exports / files.

    Governance:
        READ_ONLY = True
        LIVE_AUTO_EXECUTION = False
        ORDER_CAPABILITY = NONE
        EXECUTION_AUTHORITY = NONE
    """

    READ_ONLY = True
    LIVE_AUTO_EXECUTION = False
    ORDER_CAPABILITY = "NONE"
    EXECUTION_AUTHORITY = "NONE"

    SOURCE = "SCREENER_IN_PERSONAL_VIEW"

    def __init__(
        self,
        permission_gateway: PermissionGateway,
        data_root: Optional[str] = None,
    ):
        self.gateway = permission_gateway
        self.data_root = (
            data_root
            or rf"{ECOSYSTEM_DIR}\data_cache\screener"
        )
        os.makedirs(self.data_root, exist_ok=True)

    def _assert_read_only(self) -> None:
        if not self.READ_ONLY:
            raise RuntimeError(
                "Screener connector read-only invariant violated."
            )

        if self.LIVE_AUTO_EXECUTION:
            raise RuntimeError(
                "LIVE_AUTO_EXECUTION must remain FALSE."
            )

        if self.ORDER_CAPABILITY != "NONE":
            raise RuntimeError(
                "ORDER_CAPABILITY must remain NONE."
            )

        if self.EXECUTION_AUTHORITY != "NONE":
            raise RuntimeError(
                "EXECUTION_AUTHORITY must remain NONE."
            )

        if self.gateway is None:
            raise RuntimeError(
                "PermissionGateway is required."
            )

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _success(
        self,
        symbol: str,
        data: Dict[str, Any],
        payload_reference: str,
    ) -> Dict[str, Any]:
        return {
            "source": self.SOURCE,
            "retrieved_at": self._timestamp(),
            "symbol": symbol,
            "status": "SUCCESS",
            "read_only": True,
            "provider_payload_reference": payload_reference,
            "data": data,
        }

    def _fail_closed(
        self,
        symbol: str,
        reason: str,
        payload_reference: str = "",
    ) -> Dict[str, Any]:
        return {
            "source": self.SOURCE,
            "retrieved_at": self._timestamp(),
            "symbol": symbol,
            "status": "FAIL_CLOSED",
            "read_only": True,
            "provider_payload_reference": payload_reference,
            "data": {},
            "error": reason,
        }

    def _candidate_files(self, symbol: str) -> List[str]:
        clean_symbol = symbol.upper().strip()

        candidates = [
            os.path.join(
                self.data_root,
                f"{clean_symbol}.csv",
            ),
            os.path.join(
                self.data_root,
                f"{clean_symbol}.json",
            ),
        ]

        return [
            path
            for path in candidates
            if os.path.isfile(path)
        ]

    def _load_payload(
        self,
        symbol: str,
    ) -> tuple[Optional[Any], str]:
        candidates = self._candidate_files(symbol)

        if not candidates:
            return None, ""

        path = candidates[0]

        try:
            if path.lower().endswith(".json"):
                with open(
                    path,
                    "r",
                    encoding="utf-8",
                ) as handle:
                    return json.load(handle), path

            if path.lower().endswith(".csv"):
                with open(
                    path,
                    "r",
                    encoding="utf-8-sig",
                    newline="",
                ) as handle:
                    reader = csv.DictReader(handle)
                    rows = list(reader)

                return rows, path

        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            csv.Error,
        ) as exc:
            raise RuntimeError(
                f"Unable to read local Screener export: {exc}"
            ) from exc

        return None, ""

    @staticmethod
    def _normalize_key(value: Any) -> str:
        return (
            str(value)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )

    @classmethod
    def _flatten_payload(
        cls,
        payload: Any,
    ) -> Dict[str, Any]:
        flattened: Dict[str, Any] = {}

        if isinstance(payload, dict):
            for key, value in payload.items():
                flattened[
                    cls._normalize_key(key)
                ] = value

        elif isinstance(payload, list):
            for row in payload:
                if not isinstance(row, dict):
                    continue

                keys_lower = [
                    str(k).strip().lower()
                    for k in row.keys()
                ]

                if (
                    "metric" in keys_lower
                    and "value" in keys_lower
                ):
                    m_key = next(
                        k
                        for k in row.keys()
                        if str(k).strip().lower()
                        == "metric"
                    )

                    v_key = next(
                        k
                        for k in row.keys()
                        if str(k).strip().lower()
                        == "value"
                    )

                    metric_name = row[m_key]
                    metric_val = row[v_key]

                    if metric_name:
                        flattened[
                            cls._normalize_key(metric_name)
                        ] = metric_val

                else:
                    for key, value in row.items():
                        flattened[
                            cls._normalize_key(key)
                        ] = value

        return flattened

    @staticmethod
    def _extract(
        data: Dict[str, Any],
        aliases: List[str],
    ) -> Any:
        normalized = {
            str(key).lower(): value
            for key, value in data.items()
        }

        for alias in aliases:
            key = alias.lower()

            if key in normalized:
                return normalized[key]

        return None

    def _load_symbol_data(
        self,
        symbol: str,
    ) -> tuple[Optional[Dict[str, Any]], str]:

        clean_symbol = symbol.upper().strip()

        if not clean_symbol:
            raise ValueError(
                "symbol cannot be empty."
            )

        # 1. Preferred: consolidated Screener cache
        consolidated_candidates = [
            os.path.join(
                self.data_root,
                "screener_fundamentals.csv",
            ),
            os.path.join(
                self.data_root,
                "screener_fundamentals.json",
            ),
        ]

        for path in consolidated_candidates:

            if not os.path.isfile(path):
                continue

            try:
                # --------------------------------------------------
                # Consolidated CSV
                # --------------------------------------------------
                if path.lower().endswith(".csv"):

                    with open(
                        path,
                        "r",
                        encoding="utf-8-sig",
                        newline="",
                    ) as handle:
                        rows = list(
                            csv.DictReader(handle)
                        )

                    symbol_rows = []

                    for row in rows:
                        row_symbol = (
                            row.get("symbol")
                            or row.get("Symbol")
                            or row.get("SYMBOL")
                        )

                        if (
                            row_symbol
                            and str(row_symbol)
                            .strip()
                            .upper()
                            == clean_symbol
                        ):
                            symbol_rows.append(row)

                    if symbol_rows:

                        normalized = (
                            self._flatten_payload(
                                symbol_rows
                            )
                        )

                        if normalized:
                            return normalized, path

                # --------------------------------------------------
                # Consolidated JSON
                # --------------------------------------------------
                elif path.lower().endswith(".json"):

                    with open(
                        path,
                        "r",
                        encoding="utf-8",
                    ) as handle:
                        payload = json.load(handle)

                    # Dictionary keyed by symbol
                    if isinstance(payload, dict):

                        symbol_payload = payload.get(
                            clean_symbol
                        )

                        if symbol_payload is not None:

                            normalized = (
                                self._flatten_payload(
                                    symbol_payload
                                )
                            )

                            if normalized:
                                return normalized, path

                    # List of symbol records
                    elif isinstance(payload, list):

                        symbol_rows = []

                        for row in payload:

                            if not isinstance(row, dict):
                                continue

                            row_symbol = (
                                row.get("symbol")
                                or row.get("Symbol")
                                or row.get("SYMBOL")
                            )

                            if (
                                row_symbol
                                and str(row_symbol)
                                .strip()
                                .upper()
                                == clean_symbol
                            ):
                                symbol_rows.append(row)

                        if symbol_rows:

                            normalized = (
                                self._flatten_payload(
                                    symbol_rows
                                )
                            )

                            if normalized:
                                return normalized, path

            except (
                OSError,
                UnicodeError,
                json.JSONDecodeError,
                csv.Error,
            ) as exc:

                raise RuntimeError(
                    "Unable to read consolidated "
                    f"Screener cache: {exc}"
                ) from exc

        # 2. Fallback: existing per-symbol CSV/JSON cache
        payload, path = self._load_payload(
            clean_symbol
        )

        if payload is None:
            return None, ""

        normalized = self._flatten_payload(
            payload
        )

        if not normalized:
            return {}, path

        return normalized, path

    def get_company_fundamentals(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        self._assert_read_only()

        clean_symbol = symbol.upper().strip()

        try:
            data, path = self._load_symbol_data(
                clean_symbol
            )

        except Exception as exc:
            return self._fail_closed(
                clean_symbol,
                str(exc),
            )

        if data is None:
            return self._fail_closed(
                clean_symbol,
                "No authorized local Screener export found.",
            )

        fundamentals = {
            "market_cap": self._extract(
                data,
                [
                    "market_cap",
                    "market_capitalization",
                    "mar_cap",
                ],
            ),
            "pe": self._extract(
                data,
                [
                    "pe",
                    "p_e",
                    "price_to_earnings",
                ],
            ),
            "roce": self._extract(
                data,
                [
                    "roce",
                    "return_on_capital_employed",
                ],
            ),
            "roe": self._extract(
                data,
                [
                    "roe",
                    "return_on_equity",
                ],
            ),
            "debt_to_equity": self._extract(
                data,
                [
                    "debt_to_equity",
                    "d_e",
                ],
            ),
            "current_ratio": self._extract(
                data,
                [
                    "current_ratio",
                ],
            ),
            "quick_ratio": self._extract(
                data,
                [
                    "quick_ratio",
                ],
            ),
        }

        available = [
            key
            for key, value in fundamentals.items()
            if value is not None
        ]

        if not available:
            return self._fail_closed(
                clean_symbol,
                "No recognized fundamental fields found.",
                path,
            )

        return self._success(
            clean_symbol,
            fundamentals,
            path,
        )

    def get_financial_summary(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        self._assert_read_only()

        clean_symbol = symbol.upper().strip()

        try:
            data, path = self._load_symbol_data(
                clean_symbol
            )

        except Exception as exc:
            return self._fail_closed(
                clean_symbol,
                str(exc),
            )

        if data is None:
            return self._fail_closed(
                clean_symbol,
                "No authorized local Screener export found.",
            )

        financials = {
            "sales_growth": self._extract(
                data,
                [
                    "sales_growth",
                    "sales_growth_3years",
                    "sales_growth_5years",
                ],
            ),
            "profit_growth": self._extract(
                data,
                [
                    "profit_growth",
                    "profit_growth_3years",
                    "profit_growth_5years",
                ],
            ),
            "opm": self._extract(
                data,
                [
                    "opm",
                    "operating_profit_margin",
                ],
            ),
            "net_profit": self._extract(
                data,
                [
                    "net_profit",
                    "profit_after_tax",
                ],
            ),
            "eps": self._extract(
                data,
                [
                    "eps",
                    "eps_ttm",
                ],
            ),
        }

        available = [
            key
            for key, value in financials.items()
            if value is not None
        ]

        if not available:
            return self._fail_closed(
                clean_symbol,
                "No recognized financial-summary fields found.",
                path,
            )

        return self._success(
            clean_symbol,
            financials,
            path,
        )

    def get_quarterly_results(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        self._assert_read_only()

        clean_symbol = symbol.upper().strip()

        try:
            data, path = self._load_symbol_data(
                clean_symbol
            )

        except Exception as exc:
            return self._fail_closed(
                clean_symbol,
                str(exc),
            )

        if data is None:
            return self._fail_closed(
                clean_symbol,
                "No authorized local Screener export found.",
            )

        quarterly = {
            "sales": self._extract(
                data,
                [
                    "sales",
                    "sales_qtr",
                    "quarterly_sales",
                ],
            ),
            "sales_growth": self._extract(
                data,
                [
                    "sales_qtr_growth",
                    "sales_growth_qtr",
                    "qtr_sales_var",
                ],
            ),
            "profit": self._extract(
                data,
                [
                    "profit_qtr",
                    "quarterly_profit",
                    "net_profit_qtr",
                ],
            ),
            "profit_growth": self._extract(
                data,
                [
                    "profit_qtr_growth",
                    "profit_growth_qtr",
                    "qtr_profit_var",
                ],
            ),
        }

        available = [
            key
            for key, value in quarterly.items()
            if value is not None
        ]

        if not available:
            return self._fail_closed(
                clean_symbol,
                "No recognized quarterly-result fields found.",
                path,
            )

        return self._success(
            clean_symbol,
            quarterly,
            path,
        )

    def get_balance_sheet_summary(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        self._assert_read_only()

        clean_symbol = symbol.upper().strip()

        try:
            data, path = self._load_symbol_data(
                clean_symbol
            )

        except Exception as exc:
            return self._fail_closed(
                clean_symbol,
                str(exc),
            )

        if data is None:
            return self._fail_closed(
                clean_symbol,
                "No authorized local Screener export found.",
            )

        balance_sheet = {
            "total_assets": self._extract(
                data,
                [
                    "total_assets",
                ],
            ),
            "total_liabilities": self._extract(
                data,
                [
                    "total_liabilities",
                ],
            ),
            "reserves": self._extract(
                data,
                [
                    "reserves",
                    "reserves_surplus",
                ],
            ),
            "borrowings": self._extract(
                data,
                [
                    "borrowings",
                    "total_borrowings",
                ],
            ),
            "cash": self._extract(
                data,
                [
                    "cash",
                    "cash_equivalents",
                ],
            ),
        }

        available = [
            key
            for key, value in balance_sheet.items()
            if value is not None
        ]

        if not available:
            return self._fail_closed(
                clean_symbol,
                "No recognized balance-sheet fields found.",
                path,
            )

        return self._success(
            clean_symbol,
            balance_sheet,
            path,
        )