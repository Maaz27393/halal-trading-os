import csv
import io
import os
import sys
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"

if VAULT_ROOT not in sys.path:
    sys.path.insert(0, VAULT_ROOT)

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

from security.gateway import PermissionGateway


class KiteReadOnlyConnector:
    """
    Strict read-only Kite Connect market-data connector.

    This connector intentionally exposes only:
        - instruments()
        - quote()
        - ltp()
        - historical_data()

    No order, portfolio, GTT, margin, or execution methods are exposed.

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

    SOURCE = "KITE_CONNECT_READ_ONLY"

    BASE_URL = "https://api.kite.trade"
    API_VERSION = "3"

    # Kite API limits documented by Zerodha.
    QUOTE_MIN_INTERVAL = 1.0
    HISTORICAL_MIN_INTERVAL = 1.0 / 3.0

    # Official quote API limit.
    MAX_QUOTE_INSTRUMENTS = 500

    def __init__(
        self,
        permission_gateway: PermissionGateway,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        timeout: int = 10,
        role: str = "analyst_agent",
    ):
        self.gateway = permission_gateway
        self.role = role

        self.api_key = (
            api_key
            or os.getenv("KITE_API_KEY")
        )

        self.access_token = (
            access_token
            or os.getenv("KITE_ACCESS_TOKEN")
        )

        self.timeout = timeout

        self._session: Optional[requests.Session] = None
        self._connected = False

        self._lock = threading.Lock()
        self._last_quote_request = 0.0
        self._last_historical_request = 0.0

    # ============================================================
    # SESSION / GOVERNANCE
    # ============================================================

    def _assert_governance(self) -> None:
        if not self.READ_ONLY:
            raise RuntimeError(
                "Kite read-only invariant violated."
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

    def connect(self) -> bool:
        """
        Initialize authenticated read-only HTTP session.
        """
        self._assert_governance()

        if not self.gateway.verify_permission(
            self.role,
            "READ",
        ):
            raise PermissionError(
                f"Role '{self.role}' lacks READ permission."
            )

        if not self.api_key:
            raise RuntimeError(
                "KITE_API_KEY environment variable is required."
            )

        if not self.access_token:
            raise RuntimeError(
                "KITE_ACCESS_TOKEN environment variable is required."
            )

        if self._connected:
            return True

        session = requests.Session()

        session.headers.update(
            {
                "X-Kite-Version": self.API_VERSION,
                "Authorization": (
                    f"token {self.api_key}:{self.access_token}"
                ),
                "Accept": "application/json",
                "User-Agent": "HalalTradingOS-KiteReadOnly/1.0",
            }
        )

        self._session = session
        self._connected = True

        return True

    def close(self) -> None:
        """
        Idempotent session teardown.
        """
        with self._lock:
            if self._session is not None:
                try:
                    self._session.close()
                finally:
                    self._session = None

            self._connected = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def _require_connection(self) -> requests.Session:
        self._assert_governance()

        if not self._connected or self._session is None:
            raise ConnectionError(
                "Kite connector is not connected."
            )

        return self._session

    @staticmethod
    def _raise_for_kite_response(
        response: requests.Response,
    ) -> None:
        if response.status_code == 401:
            raise RuntimeError(
                "Kite authentication failed: invalid API key or access token."
            )

        if response.status_code == 403:
            raise RuntimeError(
                "Kite session expired or was invalidated. "
                "Refresh the access token."
            )

        if response.status_code == 429:
            raise RuntimeError(
                "Kite API rate limit exceeded."
            )

        if response.status_code >= 400:
            try:
                body = response.json()
                message = body.get(
                    "message",
                    response.text,
                )
            except ValueError:
                message = response.text

            raise RuntimeError(
                f"Kite API HTTP {response.status_code}: {message}"
            )

    def _wait_for_rate_limit(
        self,
        request_type: str,
    ) -> None:

        if request_type == "quote":
            minimum_interval = self.QUOTE_MIN_INTERVAL
        elif request_type == "historical":
            minimum_interval = self.HISTORICAL_MIN_INTERVAL
        else:
            return

        with self._lock:
            if request_type == "quote":
                last_request = self._last_quote_request
            else:
                last_request = self._last_historical_request

            elapsed = time.monotonic() - last_request

            if elapsed < minimum_interval:
                time.sleep(
                    minimum_interval - elapsed
                )

            now = time.monotonic()

            if request_type == "quote":
                self._last_quote_request = now
            else:
                self._last_historical_request = now

    def _get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        request_type: str = "other",
    ) -> requests.Response:

        session = self._require_connection()

        self._wait_for_rate_limit(request_type)

        response = session.get(
            f"{self.BASE_URL}{path}",
            params=params,
            timeout=self.timeout,
        )

        self._raise_for_kite_response(response)

        return response

    @staticmethod
    def _success(
        operation: str,
        data: Any,
    ) -> Dict[str, Any]:
        return {
            "source": KiteReadOnlyConnector.SOURCE,
            "retrieved_at": KiteReadOnlyConnector._timestamp(),
            "operation": operation,
            "status": "SUCCESS",
            "read_only": True,
            "data": data,
        }

    @staticmethod
    def _fail_closed(
        operation: str,
        reason: str,
    ) -> Dict[str, Any]:
        return {
            "source": KiteReadOnlyConnector.SOURCE,
            "retrieved_at": KiteReadOnlyConnector._timestamp(),
            "operation": operation,
            "status": "FAIL_CLOSED",
            "read_only": True,
            "data": {},
            "error": reason,
        }

    # ============================================================
    # INSTRUMENT MASTER
    # ============================================================

    def instruments(
        self,
        exchange: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve Kite instrument master.

        exchange examples:
            NSE
            BSE
            NFO

        When exchange is omitted, retrieves the complete instrument dump.
        """

        operation = "instruments"

        try:
            path = (
                f"/instruments/{exchange.upper().strip()}"
                if exchange
                else "/instruments"
            )

            response = self._get(path)

            text = response.content.decode(
                "utf-8"
            ).strip()

            reader = csv.DictReader(
                io.StringIO(text)
            )

            records: List[Dict[str, Any]] = []

            for row in reader:
                records.append(row)

            return self._success(
                operation,
                {
                    "exchange": exchange,
                    "count": len(records),
                    "instruments": records,
                },
            )

        except Exception as exc:
            return self._fail_closed(
                operation,
                str(exc),
            )

    # ============================================================
    # FULL MARKET QUOTE
    # ============================================================

    def quote(
        self,
        instruments: List[str],
    ) -> Dict[str, Any]:
        """
        Retrieve full market quotes.

        Expected format:
            ["NSE:INFY", "NSE:TCS"]

        Maximum:
            500 instruments per request.
        """

        operation = "quote"

        try:
            if not instruments:
                raise ValueError(
                    "At least one instrument is required."
                )

            clean = [
                str(item).strip().upper()
                for item in instruments
                if str(item).strip()
            ]

            if len(clean) > self.MAX_QUOTE_INSTRUMENTS:
                raise ValueError(
                    f"Quote request exceeds "
                    f"{self.MAX_QUOTE_INSTRUMENTS} instrument limit."
                )

            params = [
                ("i", instrument)
                for instrument in clean
            ]

            response = self._get(
                "/quote",
                params=params,
                request_type="quote",
            )

            body = response.json()

            return self._success(
                operation,
                body.get("data", {}),
            )

        except Exception as exc:
            return self._fail_closed(
                operation,
                str(exc),
            )

    # ============================================================
    # LTP
    # ============================================================

    def ltp(
        self,
        instruments: List[str],
    ) -> Dict[str, Any]:
        """
        Retrieve last traded price.

        Expected format:
            ["NSE:INFY", "NSE:TCS"]
        """

        operation = "ltp"

        try:
            if not instruments:
                raise ValueError(
                    "At least one instrument is required."
                )

            clean = [
                str(item).strip().upper()
                for item in instruments
                if str(item).strip()
            ]

            if len(clean) > self.MAX_QUOTE_INSTRUMENTS:
                raise ValueError(
                    f"LTP request exceeds "
                    f"{self.MAX_QUOTE_INSTRUMENTS} instrument limit."
                )

            params = [
                ("i", instrument)
                for instrument in clean
            ]

            response = self._get(
                "/quote/ltp",
                params=params,
                request_type="quote",
            )

            body = response.json()

            return self._success(
                operation,
                body.get("data", {}),
            )

        except Exception as exc:
            return self._fail_closed(
                operation,
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
        """
        Retrieve historical candles.

        Supported intervals include:
            minute
            3minute
            5minute
            10minute
            15minute
            30minute
            60minute
            day
        """

        operation = "historical_data"

        try:
            if not instrument_token:
                raise ValueError(
                    "instrument_token is required."
                )

            if not from_date or not to_date:
                raise ValueError(
                    "from_date and to_date are required."
                )

            if not interval:
                raise ValueError(
                    "interval is required."
                )

            clean_interval = interval.strip().lower()

            allowed_intervals = {
                "minute",
                "3minute",
                "5minute",
                "10minute",
                "15minute",
                "30minute",
                "60minute",
                "day",
            }

            if clean_interval not in allowed_intervals:
                raise ValueError(
                    f"Unsupported interval: {interval}"
                )

            path = (
                "/instruments/historical/"
                f"{int(instrument_token)}/"
                f"{clean_interval}"
            )

            params = {
                "from": from_date,
                "to": to_date,
                "continuous": 1 if continuous else 0,
                "oi": 1 if oi else 0,
            }

            response = self._get(
                path,
                params=params,
                request_type="historical",
            )

            body = response.json()

            return self._success(
                operation,
                {
                    "instrument_token": int(
                        instrument_token
                    ),
                    "interval": clean_interval,
                    "from": from_date,
                    "to": to_date,
                    "continuous": continuous,
                    "oi": oi,
                    "candles": body.get(
                        "data",
                        {},
                    ).get(
                        "candles",
                        [],
                    ),
                },
            )

        except Exception as exc:
            return self._fail_closed(
                operation,
                str(exc),
            )