from typing import Any, Dict, List, Optional

from security.gateway import PermissionGateway

from operational_layer.kite_registry_adapter import (
    KiteRegistryAdapter,
    build_kite_resolver,
)


class KiteOperationalAdapter:
    """
    Provider-neutral operational facade for Kite.

    The provider is resolved through CapabilityResolver.
    No execution capability is exposed.
    """

    READ_ONLY = True
    LIVE_AUTO_EXECUTION = False
    ORDER_CAPABILITY = "NONE"
    EXECUTION_AUTHORITY = "NONE"

    SOURCE = "KITE_MCP_READ_ONLY"

    def __init__(
        self,
        vault_path: str = r"D:\OBSIDIAN VAULT\halal-trading-os",
        gateway: Optional[PermissionGateway] = None,
    ):
        self.vault_path = vault_path
        self.gateway = gateway or PermissionGateway()
        self.resolver = build_kite_resolver(self.gateway)

        self.last_meta_info: Dict[str, Any] = {}
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

    def _adapter(self) -> KiteRegistryAdapter:
        self._assert_governance()

        adapter = self.resolver.resolve_adapter(
            KiteRegistryAdapter.NAMESPACE
        )

        if adapter is None:
            raise RuntimeError(
                "Kite registry adapter could not be resolved."
            )

        if not isinstance(adapter, KiteRegistryAdapter):
            raise RuntimeError(
                "Unexpected Kite registry adapter type: "
                + type(adapter).__name__
            )

        return adapter

    def _dispatch(
        self,
        method_name: str,
        required_operation: str,
        **kwargs: Any,
    ) -> Any:

        result = self.resolver.execute_via_capability(
            namespace=KiteRegistryAdapter.NAMESPACE,
            method_name=method_name,
            required_operation=required_operation,
            **kwargs,
        )

        adapter = self._adapter()

        self.last_meta_info = dict(
            adapter.last_meta_info
        )

        return result

    def connect(self) -> None:
        self._adapter().connect()

    def close(self) -> None:
        self._adapter().close()
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

    def login(
        self,
        open_browser: bool = True,
        wait_for_user: bool = True,
    ) -> Dict[str, Any]:

        result = self._adapter().login(
            open_browser=open_browser,
            wait_for_user=wait_for_user,
        )

        if result.get("status") == "SUCCESS":
            self._authenticated = True

        return result

    def ensure_authenticated(
        self,
        interactive: bool = True,
    ) -> None:

        self._adapter().ensure_authenticated(
            interactive=interactive
        )

        self._authenticated = True

    def fetch_and_adapt_ltp(
        self,
        symbols: List[str],
        exchange: str = "NSE",
        auto_login: bool = False,
    ) -> Dict[str, Any]:

        return self._dispatch(
            "fetch_and_adapt_ltp",
            "READ",
            symbols=symbols,
            exchange=exchange,
            auto_login=auto_login,
        )

    def fetch_and_adapt_quotes(
        self,
        symbols: List[str],
        exchange: str = "NSE",
        auto_login: bool = False,
    ) -> Dict[str, Any]:

        return self._dispatch(
            "fetch_and_adapt_quotes",
            "READ",
            symbols=symbols,
            exchange=exchange,
            auto_login=auto_login,
        )

    def fetch_and_adapt_ohlc(
        self,
        symbols: List[str],
        exchange: str = "NSE",
        auto_login: bool = False,
    ) -> Dict[str, Any]:

        return self._dispatch(
            "fetch_and_adapt_ohlc",
            "READ",
            symbols=symbols,
            exchange=exchange,
            auto_login=auto_login,
        )

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

        return self._dispatch(
            "fetch_and_adapt_historical",
            "READ",
            instrument_token=instrument_token,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
            continuous=continuous,
            oi=oi,
            auto_login=auto_login,
        )

    def search_instruments(
        self,
        query: str,
        filter_on: Optional[str] = None,
        from_index: Optional[int] = None,
        limit: Optional[int] = None,
        auto_login: bool = False,
    ) -> Dict[str, Any]:

        return self._dispatch(
            "search_instruments",
            "SEARCH",
            query=query,
            filter_on=filter_on,
            from_index=from_index,
            limit=limit,
            auto_login=auto_login,
        )
