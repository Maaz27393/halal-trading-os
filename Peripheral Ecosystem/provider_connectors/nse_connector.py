import sys
import logging
import requests
from typing import Dict, Any
from urllib.parse import quote


VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"

if VAULT_ROOT not in sys.path:
    sys.path.insert(0, VAULT_ROOT)

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

from security.gateway import PermissionGateway


logger = logging.getLogger("NSEConnector")


class NSEConnector:
    """
    Read-only NSE provider connector.

    v1:
        - Market status
        - Index vitals
        - India VIX

    v1.1:
        - Capital Market status/snapshot
        - Advance / Decline breadth

    Optional:
        - Equity quote

    No order placement.
    No trading actions.
    No execution authority.
    """

    READ_ONLY = True
    LIVE_AUTO_EXECUTION = False

    def __init__(self, permission_gateway: PermissionGateway):
        self.gateway = permission_gateway
        self.provenance = "LIVE_NSE_PUBLIC_REST"
        self.base_url = "https://www.nseindia.com"

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": f"{self.base_url}/",
            "Connection": "keep-alive",
        })

    # =========================================================
    # SECURITY
    # =========================================================

    def _assert_read_only(self) -> None:
        """
        Enforce connector-level read-only invariants.
        """

        if not self.READ_ONLY:
            raise RuntimeError(
                "NSE connector read-only invariant violated."
            )

        if self.LIVE_AUTO_EXECUTION:
            raise RuntimeError(
                "LIVE_AUTO_EXECUTION must remain FALSE."
            )

        if self.gateway is None:
            raise RuntimeError(
                "PermissionGateway is required for NSE connector operation."
            )

    # =========================================================
    # SESSION
    # =========================================================

    def connect(self) -> bool:
        """
        Initialize the NSE public session.
        """

        self._assert_read_only()

        logger.info("Initializing NSE public session...")

        try:
            response = self.session.get(
                self.base_url,
                timeout=15,
            )

            logger.info(
                "NSE handshake HTTP %s | cookies=%d",
                response.status_code,
                len(self.session.cookies),
            )

            return response.ok

        except requests.RequestException as exc:
            logger.warning(
                "NSE handshake warning: %s",
                exc,
            )
            return False

    def _get_json(self, path: str) -> Dict[str, Any]:
        """
        Fetch an NSE JSON endpoint using the current session.
        """

        self._assert_read_only()

        if not self.session.cookies:
            self.connect()

        url = f"{self.base_url}{path}"

        response = self.session.get(
            url,
            timeout=15,
            headers={
                "Accept": "application/json, text/plain, */*",
                "Referer": f"{self.base_url}/",
                "X-Requested-With": "XMLHttpRequest",
            },
        )

        response.raise_for_status()

        try:
            payload = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"NSE returned a non-JSON response for {path}"
            ) from exc

        if not isinstance(payload, dict):
            raise RuntimeError(
                f"NSE returned an unexpected JSON structure for {path}"
            )

        return payload

    # =========================================================
    # V1 - MARKET STATUS
    # =========================================================

    def fetch_market_status(self) -> Dict[str, Any]:
        """Fetch current NSE market status."""

        data = self._get_json("/api/marketStatus")

        return {
            "source": self.provenance,
            "capability": "market_status",
            "read_only": True,
            "status": "OK",
            "data": data,
        }

    # =========================================================
    # V1.1 - CAPITAL MARKET SNAPSHOT
    # =========================================================

    def fetch_capital_market_snapshot(self) -> Dict[str, Any]:
        """
        Fetch the explicitly identified Capital Market entry
        from the NSE marketStatus response.

        Fails closed if Capital Market cannot be identified.
        """

        self._assert_read_only()

        data = self._get_json("/api/marketStatus")

        market_states = data.get("marketState")

        if not isinstance(market_states, list):
            return {
                "source": self.provenance,
                "capability": "capital_market_snapshot",
                "read_only": True,
                "status": "UNAVAILABLE",
                "data": {},
                "validation_error": (
                    "NSE response does not contain a valid marketState list."
                ),
            }

        capital_market = None

        for item in market_states:
            if not isinstance(item, dict):
                continue

            market_name = str(
                item.get("market", "")
            ).strip()

            if "capital" in market_name.lower():
                capital_market = item
                break

        if capital_market is None:
            return {
                "source": self.provenance,
                "capability": "capital_market_snapshot",
                "read_only": True,
                "status": "UNAVAILABLE",
                "data": {},
                "validation_error": (
                    "Capital Market segment was not explicitly "
                    "identified in the NSE marketState response."
                ),
            }

        return {
            "source": self.provenance,
            "capability": "capital_market_snapshot",
            "read_only": True,
            "status": "OK",
            "timestamp": data.get("timestamp"),
            "data": {
                "market": capital_market.get("market"),
                "marketStatus": capital_market.get("marketStatus"),
                "tradeDate": capital_market.get("tradeDate"),
                "index": capital_market.get("index"),
                "last": capital_market.get("last"),
                "variation": capital_market.get("variation"),
                "percentChange": capital_market.get("percentChange"),
                "marketStatusMessage": capital_market.get(
                    "marketStatusMessage"
                ),
            },
        }

    # =========================================================
    # V1 - INDEX VITALS
    # =========================================================

    def fetch_index_vitals(
        self,
        index_name: str = "NIFTY 50",
    ) -> Dict[str, Any]:
        """Fetch a specific NSE index."""

        clean_index = index_name.upper().strip()

        if not clean_index:
            raise ValueError("index_name cannot be empty.")

        data = self._get_json("/api/allIndices")

        indices_list = data.get("data", [])

        if not isinstance(indices_list, list):
            return {
                "source": self.provenance,
                "capability": "index_vitals",
                "read_only": True,
                "status": "UNAVAILABLE",
                "index": clean_index,
                "data": {},
                "timestamp": data.get("timestamp", ""),
                "validation_error": (
                    "NSE allIndices response does not contain "
                    "a valid data list."
                ),
            }

        matched_index = None

        for item in indices_list:
            if not isinstance(item, dict):
                continue

            name = (
                item.get("index")
                or item.get("indexSymbol")
                or item.get("key")
                or ""
            )

            if str(name).upper().strip() == clean_index:
                matched_index = item
                break

        if matched_index is None:
            return {
                "source": self.provenance,
                "capability": "index_vitals",
                "read_only": True,
                "status": "UNAVAILABLE",
                "index": clean_index,
                "data": {},
                "timestamp": data.get("timestamp", ""),
                "validation_error": (
                    f"Requested index '{clean_index}' "
                    "was not explicitly found."
                ),
            }

        return {
            "source": self.provenance,
            "capability": "index_vitals",
            "read_only": True,
            "status": "OK",
            "index": clean_index,
            "data": matched_index,
            "timestamp": data.get("timestamp", ""),
        }

    # =========================================================
    # V1 - INDIA VIX
    # =========================================================

    def fetch_india_vix(self) -> Dict[str, Any]:
        """Fetch India VIX."""

        return self.fetch_index_vitals("INDIA VIX")

    # =========================================================
    # V1.1 - ADVANCE / DECLINE
    # =========================================================

    def fetch_advance_decline(self) -> Dict[str, Any]:
        """
        Fetch advance/decline breadth information.

        No fabricated zeros.
        No unrelated-record fallback.
        """

        self._assert_read_only()

        data = self._get_json("/api/allIndices")

        items = data.get("data", [])

        if not isinstance(items, list):
            return {
                "source": self.provenance,
                "capability": "advance_decline",
                "read_only": True,
                "status": "UNAVAILABLE",
                "data": {},
                "validation_error": (
                    "NSE allIndices response does not contain "
                    "a valid data list."
                ),
            }

        breadth_fields = (
            "advances",
            "declines",
            "unchanged",
        )

        # -----------------------------------------------------
        # Aggregate breadth
        # -----------------------------------------------------

        aggregate_breadth = None

        if all(
            field in data and data.get(field) is not None
            for field in breadth_fields
        ):
            aggregate_breadth = {
                "advances": data.get("advances"),
                "declines": data.get("declines"),
                "unchanged": data.get("unchanged"),
            }

        # -----------------------------------------------------
        # NIFTY 500 breadth
        # -----------------------------------------------------

        nifty_500 = None

        for item in items:
            if not isinstance(item, dict):
                continue

            index_name = str(
                item.get("index", "")
            ).upper().strip()

            if index_name == "NIFTY 500":
                nifty_500 = item
                break

        nifty_500_breadth = None

        if nifty_500 is not None:
            if all(
                field in nifty_500
                and nifty_500.get(field) is not None
                for field in breadth_fields
            ):
                nifty_500_breadth = {
                    "index": nifty_500.get("index"),
                    "advances": nifty_500.get("advances"),
                    "declines": nifty_500.get("declines"),
                    "unchanged": nifty_500.get("unchanged"),
                }

        # -----------------------------------------------------
        # Fail closed
        # -----------------------------------------------------

        if (
            aggregate_breadth is None
            and nifty_500_breadth is None
        ):
            return {
                "source": self.provenance,
                "capability": "advance_decline",
                "read_only": True,
                "status": "UNAVAILABLE",
                "timestamp": data.get("timestamp"),
                "data": {},
                "validation_error": (
                    "No recognized advance/decline breadth "
                    "fields were present in the NSE response."
                ),
            }

        result = {
            "source": self.provenance,
            "capability": "advance_decline",
            "read_only": True,
            "status": "OK",
            "timestamp": data.get("timestamp"),
            "data": {},
        }

        if aggregate_breadth is not None:
            result["data"]["aggregate_breadth"] = aggregate_breadth

        if nifty_500_breadth is not None:
            result["data"]["nifty_500_breadth"] = nifty_500_breadth

        return result

    # =========================================================
    # OPTIONAL - EQUITY QUOTE
    # =========================================================

    def fetch_equity(
        self,
        symbol: str,
    ) -> Dict[str, Any]:
        """
        Attempt an NSE equity quote.

        This remains outside the verified v1/v1.1 MCP contract.
        """

        self._assert_read_only()

        clean_symbol = symbol.upper().strip()

        if not clean_symbol:
            raise ValueError("symbol cannot be empty.")

        quote_page = (
            f"{self.base_url}/get-quotes/equity"
            f"?symbol={quote(clean_symbol)}"
        )

        try:
            page_response = self.session.get(
                quote_page,
                timeout=15,
                headers={
                    "Accept": (
                        "text/html,application/xhtml+xml,"
                        "application/xml;q=0.9,image/avif,"
                        "image/webp,*/*;q=0.8"
                    ),
                    "Referer": f"{self.base_url}/",
                    "Upgrade-Insecure-Requests": "1",
                },
            )

            logger.info(
                "Equity page handshake [%s]: HTTP %s | cookies=%d",
                clean_symbol,
                page_response.status_code,
                len(self.session.cookies),
            )

        except requests.RequestException as exc:
            logger.warning(
                "Equity page handshake warning [%s]: %s",
                clean_symbol,
                exc,
            )

        try:
            data = self._get_json(
                f"/api/quote-equity?symbol={quote(clean_symbol)}"
            )

            return {
                "source": self.provenance,
                "capability": "equity_quote",
                "read_only": True,
                "symbol": clean_symbol,
                "status": "OK",
                "data": data,
            }

        except requests.HTTPError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None
                else None
            )

            logger.error(
                "NSE equity quote failed [%s]: HTTP %s",
                clean_symbol,
                status_code,
            )

            return {
                "source": self.provenance,
                "capability": "equity_quote",
                "read_only": True,
                "symbol": clean_symbol,
                "status": "UNAVAILABLE",
                "http_status": status_code,
                "data": {},
            }

        except requests.RequestException as exc:
            logger.error(
                "NSE equity quote request failed [%s]: %s",
                clean_symbol,
                exc,
            )

            return {
                "source": self.provenance,
                "capability": "equity_quote",
                "read_only": True,
                "symbol": clean_symbol,
                "status": "UNAVAILABLE",
                "http_status": None,
                "data": {},
            }

        except RuntimeError as exc:
            logger.error(
                "NSE equity quote response invalid [%s]: %s",
                clean_symbol,
                exc,
            )

            return {
                "source": self.provenance,
                "capability": "equity_quote",
                "read_only": True,
                "symbol": clean_symbol,
                "status": "UNAVAILABLE",
                "http_status": None,
                "data": {},
                "validation_error": str(exc),
            }