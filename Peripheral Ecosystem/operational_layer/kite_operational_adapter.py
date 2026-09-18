import logging
import re
import sys
import webbrowser
from typing import Any, Dict, List, Optional

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"
PROVIDER_DIR = rf"{ECOSYSTEM_DIR}\provider_connectors"

for path in [VAULT_ROOT, ECOSYSTEM_DIR, PROVIDER_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from security.gateway import PermissionGateway
from step3_kite_mcp_connector import KiteMCPReadOnlyConnector


logger = logging.getLogger("KiteOperationalAdapter")


class KiteOperationalAdapter:
    """
    Operational adapter for the verified Kite MCP read-only connector.

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

    SOURCE = "KITE_MCP_READ_ONLY"

    def __init__(
        self,
        vault_path: str = VAULT_ROOT,
        gateway: Optional[PermissionGateway] = None,
    ):
        self.vault_path = vault_path
        self.gateway = (
            gateway
            if gateway is not None
            else PermissionGateway()
        )

        self.last_meta_info: Dict[str, Any] = {}
        self._connector: Optional[
            KiteMCPReadOnlyConnector
        ] = None
        self._authenticated = False

    def _assert_governance(self) -> None:
        if not self.READ_ONLY:
            raise RuntimeError(
                "Kite operational adapter read-only invariant violated."
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

    def connect(self) -> None:
        self._assert_governance()

        if self._connector is None:
            self._connector = KiteMCPReadOnlyConnector(
                self.gateway
            )

        self._connector.connect()

    def close(self) -> None:
        if self._connector is not None:
            self._connector.close()

        self._connector = None
        self._authenticated = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.close()
        return False

    def _client(self) -> KiteMCPReadOnlyConnector:
        self.connect()

        if self._connector is None:
            raise RuntimeError(
                "Kite MCP connector is unavailable."
            )

        return self._connector

    @staticmethod
    def _extract_login_url(
        message: str,
    ) -> str:
        match = re.search(
            r"https://mcp\.kite\.trade/authorize\?session_id=[^\s\)]+",
            message,
        )

        if not match:
            return ""

        return match.group(0)

    def login(
        self,
        open_browser: bool = True,
        wait_for_user: bool = True,
    ) -> Dict[str, Any]:
        """
        Authenticate Kite inside the current persistent MCP session.

        This is the only interactive authentication step.

        It does not expose or perform any order capability.
        """

        self._assert_governance()

        connector = self._client()

        result = connector.login()

        if result.get("status") != "SUCCESS":
            return result

        message = (
            result
            .get("data", {})
            .get("message", "")
        )

        login_url = self._extract_login_url(
            message
        )

        if login_url and open_browser:
            webbrowser.open(
                login_url
            )

        if login_url:
            print("\nKite authorization URL:")
            print(login_url)
            print(
                "\nComplete Zerodha login and 2FA "
                "in the browser."
            )

        if wait_for_user and login_url:
            input(
                "\nPress ENTER after Zerodha authorization "
                "is complete..."
            )

        self._authenticated = True

        return {
            "source": self.SOURCE,
            "status": "SUCCESS",
            "read_only": True,
            "operation": "login",
            "data": {
                "authenticated": True,
                "authorization_url_present": bool(
                    login_url
                ),
            },
        }

    def ensure_authenticated(
        self,
        interactive: bool = True,
    ) -> None:
        """
        Confirm that the current persistent MCP session is
        authenticated.

        With interactive=True, performs login when required.
        """

        self.connect()

        connector = self._client()

        probe = connector.ltp(
            ["NSE:INFY"]
        )

        if probe.get("status") == "SUCCESS":
            self._authenticated = True
            return

        error = str(
            probe.get(
                "error",
                "",
            )
        )

        if (
            "log in first" in error.lower()
            or "login required" in error.lower()
            or "not authenticated" in error.lower()
        ):
            if not interactive:
                raise RuntimeError(
                    "Kite MCP session is not authenticated."
                )

            self.login(
                open_browser=True,
                wait_for_user=True,
            )

            verify = connector.ltp(
                ["NSE:INFY"]
            )

            if verify.get("status") != "SUCCESS":
                raise RuntimeError(
                    "Kite authentication completed, "
                    "but the market-data session is still "
                    "not authenticated: "
                    + str(
                        verify.get(
                            "error",
                            "unknown error",
                        )
                    )
                )

            self._authenticated = True
            return

        raise RuntimeError(
            "Unable to verify Kite authentication: "
            + error
        )

    def fetch_and_adapt_ltp(
        self,
        symbols: List[str],
        exchange: str = "NSE",
        auto_login: bool = False,
    ) -> Dict[str, Any]:

        self._assert_governance()

        if not symbols:
            return {
                "source": self.SOURCE,
                "status": "SUCCESS_EMPTY",
                "read_only": True,
                "operation": "ltp",
                "data": {},
                "provenance": self.SOURCE,
            }

        if auto_login:
            self.ensure_authenticated(
                interactive=True
            )

        result = self._client().ltp(
            [
                f"{exchange.upper().strip()}:{str(symbol).upper().strip()}"
                for symbol in symbols
                if str(symbol).strip()
            ]
        )

        self.last_meta_info = {
            "operation": "ltp",
            "symbol_count": len(symbols),
        }

        return result

    def fetch_and_adapt_quotes(
        self,
        symbols: List[str],
        exchange: str = "NSE",
        auto_login: bool = False,
    ) -> Dict[str, Any]:

        self._assert_governance()

        if not symbols:
            return {
                "source": self.SOURCE,
                "status": "SUCCESS_EMPTY",
                "read_only": True,
                "operation": "quote",
                "data": {},
                "provenance": self.SOURCE,
            }

        if auto_login:
            self.ensure_authenticated(
                interactive=True
            )

        result = self._client().quote(
            [
                f"{exchange.upper().strip()}:{str(symbol).upper().strip()}"
                for symbol in symbols
                if str(symbol).strip()
            ]
        )

        self.last_meta_info = {
            "operation": "quote",
            "symbol_count": len(symbols),
        }

        return result

    def fetch_and_adapt_ohlc(
        self,
        symbols: List[str],
        exchange: str = "NSE",
        auto_login: bool = False,
    ) -> Dict[str, Any]:

        self._assert_governance()

        if not symbols:
            return {
                "source": self.SOURCE,
                "status": "SUCCESS_EMPTY",
                "read_only": True,
                "operation": "ohlc",
                "data": {},
                "provenance": self.SOURCE,
            }

        if auto_login:
            self.ensure_authenticated(
                interactive=True
            )

        result = self._client().ohlc(
            [
                f"{exchange.upper().strip()}:{str(symbol).upper().strip()}"
                for symbol in symbols
                if str(symbol).strip()
            ]
        )

        self.last_meta_info = {
            "operation": "ohlc",
            "symbol_count": len(symbols),
        }

        return result

    def fetch_and_adapt_historical(
        self,
        instrument_token: int,
        from_date: str,
        to_date: str,
        interval: str,
        continuous: bool = False,
        oi: bool = False,
        auto_login: bool = False,
    ) -> Dict[str, Any]:

        self._assert_governance()

        if auto_login:
            self.ensure_authenticated(
                interactive=True
            )

        result = self._client().historical_data(
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
            continuous=continuous,
            oi=oi,
        )

        self.last_meta_info = {
            "operation": "historical_data",
            "instrument_token": instrument_token,
            "interval": interval,
        }

        return result

    def search_instruments(
        self,
        query: str,
        filter_on: Optional[str] = None,
        from_index: Optional[int] = None,
        limit: Optional[int] = None,
        auto_login: bool = False,
    ) -> Dict[str, Any]:

        self._assert_governance()

        if auto_login:
            self.ensure_authenticated(
                interactive=True
            )

        result = self._client().search_instruments(
            query=query,
            filter_on=filter_on,
            from_index=from_index,
            limit=limit,
        )

        self.last_meta_info = {
            "operation": "search_instruments",
            "query": query,
        }

        return result