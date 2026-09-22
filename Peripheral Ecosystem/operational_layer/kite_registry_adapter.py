import logging
import re
import webbrowser
from typing import Any, Dict, List, Optional

from registry.models import ProviderRegistration
from registry.resolver import CapabilityResolver
from security.gateway import PermissionGateway
from provider_connectors.step3_kite_mcp_connector import (
    KiteMCPReadOnlyConnector,
)

logger = logging.getLogger("KiteRegistryAdapter")


class KiteRegistryAdapter:
    """
    Registry-facing adapter for the verified Kite MCP read-only connector.

    No order capability is exposed.
    """

    PROVIDER_ID = "kite_mcp_read_only"
    NAMESPACE = "market.kite"

    READ_ONLY = True
    LIVE_AUTO_EXECUTION = False
    ORDER_CAPABILITY = "NONE"
    EXECUTION_AUTHORITY = "NONE"

    SOURCE = "KITE_MCP_READ_ONLY"

    def __init__(
        self,
        gateway: Optional[PermissionGateway] = None,
    ):
        self.gateway = gateway or PermissionGateway()
        self.last_meta_info: Dict[str, Any] = {}
        self._connector: Optional[KiteMCPReadOnlyConnector] = None
        self._authenticated = False

    def capabilities(self) -> List[str]:
        return ["READ", "SEARCH"]

    def health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "provider_id": self.PROVIDER_ID,
            "namespace": self.NAMESPACE,
            "capabilities": self.capabilities(),
            "read_only": True,
            "live_auto_execution": False,
            "order_capability": "NONE",
            "execution_authority": "NONE",
        }

    def _assert_governance(self) -> None:
        if not self.READ_ONLY:
            raise RuntimeError("Kite READ_ONLY invariant violated.")

        if self.LIVE_AUTO_EXECUTION:
            raise RuntimeError(
                "Kite LIVE_AUTO_EXECUTION must remain FALSE."
            )

        if self.ORDER_CAPABILITY != "NONE":
            raise RuntimeError(
                "Kite ORDER_CAPABILITY must remain NONE."
            )

        if self.EXECUTION_AUTHORITY != "NONE":
            raise RuntimeError(
                "Kite EXECUTION_AUTHORITY must remain NONE."
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
    def _extract_login_url(message: str) -> str:
        match = re.search(
            r"https://mcp\.kite\.trade/authorize\?session_id=[^\s\)]+",
            message,
        )

        return match.group(0) if match else ""

    def login(
        self,
        open_browser: bool = True,
        wait_for_user: bool = True,
    ) -> Dict[str, Any]:

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

        login_url = self._extract_login_url(message)

        if login_url and open_browser:
            webbrowser.open(login_url)

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
                "authorization_url_present": bool(login_url),
            },
        }

    def ensure_authenticated(
        self,
        interactive: bool = True,
    ) -> None:

        self.connect()

        connector = self._client()

        probe = connector.ltp(["NSE:INFY"])

        if probe.get("status") == "SUCCESS":
            self._authenticated = True
            return

        error = str(
            probe.get("error", "")
        )

        auth_error = (
            "log in first" in error.lower()
            or "login required" in error.lower()
            or "not authenticated" in error.lower()
        )

        if not auth_error:
            raise RuntimeError(
                "Unable to verify Kite authentication: "
                + error
            )

        if not interactive:
            raise RuntimeError(
                "Kite MCP session is not authenticated."
            )

        self.login(
            open_browser=True,
            wait_for_user=True,
        )

        verify = connector.ltp(["NSE:INFY"])

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

    def _prepare_symbols(
        self,
        symbols: List[str],
        exchange: str,
    ) -> List[str]:

        return [
            f"{exchange.upper().strip()}:{str(symbol).upper().strip()}"
            for symbol in symbols
            if str(symbol).strip()
        ]

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
            self.ensure_authenticated(interactive=True)

        result = self._client().ltp(
            self._prepare_symbols(symbols, exchange)
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
            self.ensure_authenticated(interactive=True)

        result = self._client().quote(
            self._prepare_symbols(symbols, exchange)
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
            self.ensure_authenticated(interactive=True)

        result = self._client().ohlc(
            self._prepare_symbols(symbols, exchange)
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
            self.ensure_authenticated(interactive=True)

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
            self.ensure_authenticated(interactive=True)

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


def build_kite_resolver(
    gateway: Optional[PermissionGateway] = None,
) -> CapabilityResolver:

    resolver = CapabilityResolver()

    adapter = KiteRegistryAdapter(
        gateway=gateway
    )

    registration = ProviderRegistration(
        provider_id=adapter.PROVIDER_ID,
        namespace=adapter.NAMESPACE,
        adapter_instance=adapter,
        priority=10,
        enabled=True,
        health_status="healthy",
        supported_operations=[
            "READ",
            "SEARCH",
        ],
        metadata={
            "provider_type": "kite_mcp",
            "read_only": True,
            "order_capability": "NONE",
            "execution_authority": "NONE",
            "live_auto_execution": False,
        },
    )

    resolver.register_provider(registration)

    return resolver
