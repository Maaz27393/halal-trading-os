import asyncio
import json
import os
import shutil
import sys
import threading
from concurrent.futures import Future
from typing import Any, Dict, List, Optional, Set

from mcp import Client, StdioServerParameters

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"

if VAULT_ROOT not in sys.path:
    sys.path.insert(0, VAULT_ROOT)

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

from security.gateway import PermissionGateway


class KiteMCPReadOnlyConnector:
    """
    Persistent read-only Kite MCP connector.

    One connector instance maintains one MCP session.

    Allowed tools:
        login
        get_ltp
        get_quotes
        get_ohlc
        get_historical_data
        search_instruments

    All other Kite tools are explicitly filtered.

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

    MCP_URL = "https://mcp.kite.trade/mcp"
    MCP_REMOTE_PACKAGE = "mcp-remote@0.14.2"

    ALLOWED_DATA_TOOLS = {
        "get_ltp",
        "get_quotes",
        "get_ohlc",
        "get_historical_data",
        "search_instruments",
    }

    INTERNAL_TOOL = "login"

    BLOCKED_TOOLS = {
        "place_order",
        "modify_order",
        "cancel_order",
        "place_gtt_order",
        "modify_gtt_order",
        "delete_gtt_order",
        "get_gtts",
        "get_holdings",
        "get_margins",
        "get_mf_holdings",
        "get_order_history",
        "get_order_trades",
        "get_orders",
        "get_positions",
        "get_profile",
        "get_trades",
    }

    ALLOWED_SESSION_TOOLS = (
        ALLOWED_DATA_TOOLS | {INTERNAL_TOOL}
    )

    def __init__(
        self,
        permission_gateway: PermissionGateway,
        auth_timeout: int = 600,
        role: str = "analyst_agent",
        operation_timeout: int = 180,
    ):
        self.gateway = permission_gateway
        self.auth_timeout = auth_timeout
        self.role = role
        self.operation_timeout = operation_timeout

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._client: Optional[Client] = None
        self._client_context = None

        self._stop_event: Optional[asyncio.Event] = None
        self._ready = threading.Event()

        self._startup_error: Optional[BaseException] = None
        self._connected = False
        self._tool_names: Set[str] = set()

        self.last_login_response: str = ""

    # ============================================================
    # GOVERNANCE
    # ============================================================

    def _assert_governance(self) -> None:
        if not self.READ_ONLY:
            raise RuntimeError(
                "Kite MCP read-only invariant violated."
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

        if not self.gateway.verify_permission(
            self.role,
            "READ",
        ):
            raise PermissionError(
                f"Role '{self.role}' lacks READ permission."
            )

    # ============================================================
    # PROCESS CONFIGURATION
    # ============================================================

    @staticmethod
    def _find_npx() -> str:
        for command in ("npx.cmd", "npx"):
            resolved = shutil.which(command)

            if resolved:
                return resolved

        raise RuntimeError(
            "npx was not found on PATH."
        )

    def _server_parameters(
        self,
    ) -> StdioServerParameters:

        npx = self._find_npx()

        return StdioServerParameters(
            command=npx,
            args=[
                "-y",
                self.MCP_REMOTE_PACKAGE,
                self.MCP_URL,
                "--auth-timeout",
                str(self.auth_timeout),

                # Execution / GTT tools
                "--ignore-tool",
                "place*",
                "--ignore-tool",
                "modify*",
                "--ignore-tool",
                "cancel*",
                "--ignore-tool",
                "delete*",

                # Non-market account / order-history tools
                "--ignore-tool",
                "get_gtts",
                "--ignore-tool",
                "get_holdings",
                "--ignore-tool",
                "get_margins",
                "--ignore-tool",
                "get_mf_holdings",
                "--ignore-tool",
                "get_order_history",
                "--ignore-tool",
                "get_order_trades",
                "--ignore-tool",
                "get_orders",
                "--ignore-tool",
                "get_positions",
                "--ignore-tool",
                "get_profile",
                "--ignore-tool",
                "get_trades",
            ],
            env={
                "PATH": os.environ.get(
                    "PATH",
                    "",
                ),
            },
        )

    # ============================================================
    # ASYNC SESSION LIFECYCLE
    # ============================================================

    async def _session_main(self) -> None:
        self._stop_event = asyncio.Event()

        try:
            self._client_context = Client(
                self._server_parameters()
            )

            self._client = await (
                self._client_context.__aenter__()
            )

            tool_result = await self._client.list_tools()

            self._tool_names = {
                str(
                    getattr(
                        tool,
                        "name",
                        "",
                    )
                )
                for tool in getattr(
                    tool_result,
                    "tools",
                    [],
                )
            }

            # Strict surface verification.
            unexpected = (
                self._tool_names
                - self.ALLOWED_SESSION_TOOLS
            )

            if unexpected:
                raise RuntimeError(
                    "Kite MCP security surface violation. "
                    "Unexpected tools exposed: "
                    + ", ".join(
                        sorted(unexpected)
                    )
                )

            exposed_blocked = (
                self._tool_names
                & self.BLOCKED_TOOLS
            )

            if exposed_blocked:
                raise RuntimeError(
                    "Kite MCP security surface violation. "
                    "Blocked tools exposed: "
                    + ", ".join(
                        sorted(exposed_blocked)
                    )
                )

            missing_required = (
                self.ALLOWED_DATA_TOOLS
                - self._tool_names
            )

            if missing_required:
                raise RuntimeError(
                    "Required Kite MCP tools missing: "
                    + ", ".join(
                        sorted(missing_required)
                    )
                )

            self._connected = True
            self._ready.set()

            await self._stop_event.wait()

        except BaseException as exc:
            self._startup_error = exc
            self._ready.set()

        finally:
            self._connected = False

            if self._client_context is not None:
                try:
                    await self._client_context.__aexit__(
                        None,
                        None,
                        None,
                    )
                except Exception:
                    pass

            self._client = None
            self._client_context = None

    def connect(self) -> bool:
        """
        Start one persistent MCP session.
        """

        self._assert_governance()

        if self._connected:
            return True

        self._startup_error = None
        self._ready.clear()

        self._loop = asyncio.new_event_loop()

        def runner() -> None:
            asyncio.set_event_loop(
                self._loop
            )

            try:
                self._loop.run_until_complete(
                    self._session_main()
                )
            finally:
                self._loop.close()

        self._thread = threading.Thread(
            target=runner,
            name="kite-mcp-session",
            daemon=True,
        )

        self._thread.start()

        ready = self._ready.wait(
            timeout=30
        )

        if not ready:
            raise RuntimeError(
                "Timed out starting Kite MCP session."
            )

        if self._startup_error is not None:
            error = self._startup_error
            self._startup_error = None
            raise RuntimeError(
                f"Unable to start Kite MCP session: {error}"
            ) from error

        if not self._connected:
            raise RuntimeError(
                "Kite MCP session did not connect."
            )

        return True

    async def _shutdown_async(self) -> None:
        if self._stop_event is not None:
            self._stop_event.set()

    def close(self) -> None:
        """
        Idempotent persistent-session teardown.
        """

        if self._loop is not None:
            try:
                future = asyncio.run_coroutine_threadsafe(
                    self._shutdown_async(),
                    self._loop,
                )

                future.result(
                    timeout=10
                )
            except Exception:
                pass

        if self._thread is not None:
            self._thread.join(
                timeout=10
            )

        self._thread = None
        self._loop = None
        self._client = None
        self._connected = False
        self._tool_names = set()

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

    # ============================================================
    # ASYNC TOOL CALL
    # ============================================================

    async def _call_tool_async(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Any:

        if self._client is None:
            raise RuntimeError(
                "Kite MCP client is not connected."
            )

        if tool_name not in (
            self.ALLOWED_SESSION_TOOLS
        ):
            raise PermissionError(
                f"Kite MCP tool '{tool_name}' "
                "is not allowlisted."
            )

        if tool_name in self.BLOCKED_TOOLS:
            raise PermissionError(
                f"Kite MCP tool '{tool_name}' "
                "is explicitly blocked."
            )

        result = await self._client.call_tool(
            tool_name,
            arguments,
        )

        return result

    def _call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Any:

        self.connect()

        if self._loop is None:
            raise RuntimeError(
                "Kite MCP event loop is unavailable."
            )

        future: Future = (
            asyncio.run_coroutine_threadsafe(
                self._call_tool_async(
                    tool_name,
                    arguments,
                ),
                self._loop,
            )
        )

        return future.result(
            timeout=self.operation_timeout
        )

    # ============================================================
    # RESULT PARSING
    # ============================================================

    @staticmethod
    def _extract_text(
        result: Any,
    ) -> str:

        content = getattr(
            result,
            "content",
            [],
        )

        texts: List[str] = []

        for item in content:
            value = getattr(
                item,
                "text",
                None,
            )

            if value:
                texts.append(
                    str(value)
                )

        return "\n".join(texts)

    @classmethod
    def _extract_data(
        cls,
        result: Any,
    ) -> Any:

        structured = getattr(
            result,
            "structured_content",
            None,
        )

        if structured is not None:
            return structured

        text = cls._extract_text(
            result
        )

        if not text:
            return {}

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "text": text
            }

    @staticmethod
    def _error_result(
        operation: str,
        error: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        result = {
            "source": KiteMCPReadOnlyConnector.SOURCE,
            "status": "FAIL_CLOSED",
            "read_only": True,
            "operation": operation,
            "data": {},
            "error": error,
        }

        if extra:
            result.update(extra)

        return result

    # ============================================================
    # LOGIN
    # ============================================================

    def login(self) -> Dict[str, Any]:
        """
        Start Kite MCP login inside the persistent session.

        This does not execute any market/trading action.
        """

        self._assert_governance()

        try:
            result = self._call_tool(
                self.INTERNAL_TOOL,
                {},
            )

            text = self._extract_text(
                result
            )

            self.last_login_response = text

            return {
                "source": self.SOURCE,
                "status": (
                    "SUCCESS"
                    if not getattr(
                        result,
                        "is_error",
                        False,
                    )
                    else "FAIL_CLOSED"
                ),
                "read_only": True,
                "operation": "login",
                "data": {
                    "message": text,
                },
            }

        except Exception as exc:
            return self._error_result(
                "login",
                str(exc),
            )

    # ============================================================
    # LTP
    # ============================================================

    def ltp(
        self,
        instruments: List[str],
    ) -> Dict[str, Any]:

        self._assert_governance()

        if not instruments:
            return {
                "source": self.SOURCE,
                "status": "SUCCESS_EMPTY",
                "read_only": True,
                "operation": "ltp",
                "data": {},
            }

        try:
            result = self._call_tool(
                "get_ltp",
                {
                    "instruments": instruments,
                },
            )

            if getattr(
                result,
                "is_error",
                False,
            ):
                return self._error_result(
                    "ltp",
                    self._extract_text(
                        result
                    ),
                )

            return {
                "source": self.SOURCE,
                "status": "SUCCESS",
                "read_only": True,
                "operation": "ltp",
                "data": self._extract_data(
                    result
                ),
            }

        except Exception as exc:
            return self._error_result(
                "ltp",
                str(exc),
            )

    # ============================================================
    # FULL QUOTE
    # ============================================================

    def quote(
        self,
        instruments: List[str],
    ) -> Dict[str, Any]:

        self._assert_governance()

        if not instruments:
            return {
                "source": self.SOURCE,
                "status": "SUCCESS_EMPTY",
                "read_only": True,
                "operation": "quote",
                "data": {},
            }

        try:
            result = self._call_tool(
                "get_quotes",
                {
                    "instruments": instruments,
                },
            )

            if getattr(
                result,
                "is_error",
                False,
            ):
                return self._error_result(
                    "quote",
                    self._extract_text(
                        result
                    ),
                )

            return {
                "source": self.SOURCE,
                "status": "SUCCESS",
                "read_only": True,
                "operation": "quote",
                "data": self._extract_data(
                    result
                ),
            }

        except Exception as exc:
            return self._error_result(
                "quote",
                str(exc),
            )

    # ============================================================
    # OHLC
    # ============================================================

    def ohlc(
        self,
        instruments: List[str],
    ) -> Dict[str, Any]:

        self._assert_governance()

        if not instruments:
            return {
                "source": self.SOURCE,
                "status": "SUCCESS_EMPTY",
                "read_only": True,
                "operation": "ohlc",
                "data": {},
            }

        try:
            result = self._call_tool(
                "get_ohlc",
                {
                    "instruments": instruments,
                },
            )

            if getattr(
                result,
                "is_error",
                False,
            ):
                return self._error_result(
                    "ohlc",
                    self._extract_text(
                        result
                    ),
                )

            return {
                "source": self.SOURCE,
                "status": "SUCCESS",
                "read_only": True,
                "operation": "ohlc",
                "data": self._extract_data(
                    result
                ),
            }

        except Exception as exc:
            return self._error_result(
                "ohlc",
                str(exc),
            )

    # ============================================================
    # HISTORICAL DATA
    # ============================================================

    def historical_data(
        self,
        instrument_token: int,
        from_date: str,
        to_date: str,
        interval: str,
        continuous: bool = False,
        oi: bool = False,
    ) -> Dict[str, Any]:

        self._assert_governance()

        try:
            result = self._call_tool(
                "get_historical_data",
                {
                    "instrument_token": int(
                        instrument_token
                    ),
                    "from_date": from_date,
                    "to_date": to_date,
                    "interval": interval,
                    "continuous": continuous,
                    "oi": oi,
                },
            )

            if getattr(
                result,
                "is_error",
                False,
            ):
                return self._error_result(
                    "historical_data",
                    self._extract_text(
                        result
                    ),
                )

            return {
                "source": self.SOURCE,
                "status": "SUCCESS",
                "read_only": True,
                "operation": "historical_data",
                "data": self._extract_data(
                    result
                ),
            }

        except Exception as exc:
            return self._error_result(
                "historical_data",
                str(exc),
            )

    # ============================================================
    # INSTRUMENT SEARCH
    # ============================================================

    def search_instruments(
        self,
        query: str,
        filter_on: Optional[str] = None,
        from_index: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:

        self._assert_governance()

        if not query or not query.strip():
            return self._error_result(
                "search_instruments",
                "query is required.",
            )

        arguments: Dict[str, Any] = {
            "query": query.strip(),
        }

        if filter_on:
            arguments["filter_on"] = filter_on

        if from_index is not None:
            arguments["from"] = int(
                from_index
            )

        if limit is not None:
            arguments["limit"] = int(
                limit
            )

        try:
            result = self._call_tool(
                "search_instruments",
                arguments,
            )

            if getattr(
                result,
                "is_error",
                False,
            ):
                return self._error_result(
                    "search_instruments",
                    self._extract_text(
                        result
                    ),
                )

            return {
                "source": self.SOURCE,
                "status": "SUCCESS",
                "read_only": True,
                "operation": "search_instruments",
                "data": self._extract_data(
                    result
                ),
            }

        except Exception as exc:
            return self._error_result(
                "search_instruments",
                str(exc),
            )