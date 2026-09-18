import os
import sys
import json
import html
import time
import logging
import requests
from typing import List, Dict, Any, Tuple

from bs4 import BeautifulSoup
from pydantic import BaseModel
from playwright.sync_api import sync_playwright

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"

if VAULT_ROOT not in sys.path:
    sys.path.insert(0, VAULT_ROOT)

ECOSYSTEM_DIR = os.path.join(
    VAULT_ROOT,
    "Peripheral Ecosystem",
)

PROVIDER_DIR = os.path.join(
    ECOSYSTEM_DIR,
    "provider_connectors",
)

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

if PROVIDER_DIR not in sys.path:
    sys.path.insert(0, PROVIDER_DIR)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from provider_connectors.auth_session_provider import (
    ChartinkAuthSessionProvider,
)

logger = logging.getLogger(
    "ChartinkScannerConnector"
)


class TechnicalCandidate(BaseModel):
    symbol: str
    company_name: str
    close_price: float
    volume: int
    per_change: float
    is_halal_confirmed: bool = True
    has_execution_payload: bool = False


class ChartinkScannerConnector:
    """
    Production Chartink connector.

    Flow:

        Account-owned saved scanner
                ↓
        Raw scanner HTML
                ↓
        <scanner :scan-json>
                ↓
        Exact atlas_query
                ↓
        Authenticated Playwright session
                ↓
        CSRF from SAME browser session
                ↓
        POST /screener/process
                ↓
        Chartink JSON results
                ↓
        Canonical Halal universe intersection

    Constraints:
        - No generic scanner query
        - No fallback scanner query
        - No provider-side query reconstruction
        - No execution authority
        - LIVE_AUTO_EXECUTION must remain FALSE
    """

    def __init__(
        self,
        permission_gateway: PermissionGateway = None,
    ):
        self.gateway = permission_gateway
        self.provenance = (
            "LIVE_AUTHENTICATED_PLAYWRIGHT"
        )

        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    # ------------------------------------------------------------------
    # CONTEXT MANAGER
    # ------------------------------------------------------------------

    def __enter__(self):
        self.connect()
        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):
        self.close()
        return False

    # ------------------------------------------------------------------
    # CONNECTION
    # ------------------------------------------------------------------

    def connect(self):
        """
        Initialize authenticated Playwright session.

        Authentication cookies are loaded from the existing
        ChartinkAuthSessionProvider.
        """

        if self._page is not None:
            return

        if LIVE_AUTO_EXECUTION:
            raise RuntimeError(
                "CRITICAL SAFETY BLOCK: "
                "LIVE_AUTO_EXECUTION must remain FALSE."
            )

        logger.info(
            "Initializing authenticated Playwright session for Chartink..."
        )

        try:
            auth_provider = (
                ChartinkAuthSessionProvider()
            )

            session_cookies = (
                auth_provider.load_session_cookies()
            )

            if not session_cookies:
                raise RuntimeError(
                    "CRITICAL: No authenticated "
                    "Chartink session cookies available."
                )

            self._playwright = (
                sync_playwright().start()
            )

            self._browser = (
                self._playwright.chromium.launch(
                    headless=True
                )
            )

            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )

            self._context = (
                self._browser.new_context(
                    user_agent=user_agent
                )
            )

            cookie_list = []

            for name, value in session_cookies.items():

                if not name or value is None:
                    continue

                cookie_list.append(
                    {
                        "name": str(name),
                        "value": str(value),
                        "domain": ".chartink.com",
                        "path": "/",
                    }
                )

            if not cookie_list:
                raise RuntimeError(
                    "CRITICAL: Chartink session cookie "
                    "conversion produced no cookies."
                )

            self._context.add_cookies(
                cookie_list
            )

            self._page = (
                self._context.new_page()
            )

            logger.info(
                "Authenticated Chartink Playwright "
                "session initialized."
            )

        except Exception as exc:

            self.close()

            logger.error(
                "CRITICAL: Failed to initialize "
                "Chartink session: %s",
                exc,
            )

            raise RuntimeError(
                "Chartink Playwright initialization error: "
                f"{exc}"
            ) from exc

    # ------------------------------------------------------------------
    # CLOSE
    # ------------------------------------------------------------------

    def close(self):
        """
        Safely and idempotently release Playwright resources.

        Shutdown order:
            Page
            Context
            Browser
            Playwright
        """

        resources = [
            ("page", self._page),
            ("context", self._context),
            ("browser", self._browser),
        ]

        for resource_name, resource in resources:

            if resource is None:
                continue

            try:
                resource.close()

            except Exception as exc:

                logger.debug(
                    "Chartink %s cleanup warning: %s",
                    resource_name,
                    exc,
                )

        if self._playwright is not None:

            try:
                self._playwright.stop()

            except Exception as exc:

                logger.debug(
                    "Chartink Playwright cleanup warning: %s",
                    exc,
                )

        self._page = None
        self._context = None
        self._browser = None
        self._playwright = None

    # ------------------------------------------------------------------
    # RAW SCANNER HTML
    # ------------------------------------------------------------------

    def _get_raw_scanner_html(
        self,
        scanner_url: str,
    ) -> str:
        """
        Retrieve raw scanner HTML using the existing authenticated
        session cookies.

        This request is used to obtain the exact saved scanner
        atlas_query.

        CSRF from this requests session is NOT reused for the
        Playwright POST.
        """

        auth_provider = (
            ChartinkAuthSessionProvider()
        )

        session_cookies = (
            auth_provider.load_session_cookies()
        )

        if not session_cookies:
            raise RuntimeError(
                "CRITICAL: No Chartink authentication "
                "cookies available."
            )

        session = requests.Session()

        for name, value in session_cookies.items():

            if value is not None:

                session.cookies.set(
                    name,
                    str(value),
                    domain=".chartink.com",
                )

        response = session.get(
            scanner_url,
            timeout=60,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/131.0.0.0 "
                    "Safari/537.36"
                ),
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "*/*;q=0.8"
                ),
            },
        )

        if response.status_code != 200:

            raise RuntimeError(
                "Chartink scanner page returned "
                f"HTTP {response.status_code}: "
                f"{scanner_url}"
            )

        if not response.text:

            raise RuntimeError(
                "CRITICAL: Empty scanner HTML received: "
                f"{scanner_url}"
            )

        logger.info(
            "Raw scanner HTML loaded successfully: "
            "%s bytes",
            len(response.text),
        )

        return response.text

    # ------------------------------------------------------------------
    # EXTRACT EXACT ATLAS QUERY
    # ------------------------------------------------------------------

    def _extract_atlas_query(
        self,
        scanner_url: str,
        raw_html: str,
    ) -> str:
        """
        Extract the exact atlas_query from the account-owned
        scanner's <scanner :scan-json> metadata.

        No fallback query is permitted.
        """

        soup = BeautifulSoup(
            raw_html,
            "html.parser",
        )

        scanner_element = soup.find(
            lambda tag:
                tag.name == "scanner"
                and tag.has_attr(":scan-json")
        )

        if scanner_element is None:

            raise RuntimeError(
                "CRITICAL: <scanner :scan-json> "
                "not found: "
                f"{scanner_url}"
            )

        raw_scan_json = scanner_element.get(
            ":scan-json"
        )

        if not raw_scan_json:

            raise RuntimeError(
                "CRITICAL: Empty :scan-json "
                "attribute: "
                f"{scanner_url}"
            )

        try:

            scan_json = json.loads(
                html.unescape(
                    raw_scan_json
                )
            )

        except Exception as exc:

            raise RuntimeError(
                "CRITICAL: Failed to parse Chartink "
                "scan-json: "
                f"{exc}"
            ) from exc

        if not isinstance(
            scan_json,
            dict,
        ):

            raise RuntimeError(
                "CRITICAL: Chartink scan-json "
                "is not an object: "
                f"{scanner_url}"
            )

        atlas_query = scan_json.get(
            "atlas_query"
        )

        if not atlas_query:

            raise RuntimeError(
                "CRITICAL: atlas_query missing "
                "from account-owned scanner metadata: "
                f"{scanner_url}"
            )

        atlas_query = str(
            atlas_query
        ).strip()

        if not atlas_query:

            raise RuntimeError(
                "CRITICAL: atlas_query is empty: "
                f"{scanner_url}"
            )

        logger.info(
            "Extracted exact Chartink scanner metadata | "
            "Name=%s | ID=%s | QueryLength=%s",
            scan_json.get("name"),
            scan_json.get("id"),
            len(atlas_query),
        )

        return atlas_query

    # ------------------------------------------------------------------
    # ACTIVE BROWSER CSRF
    # ------------------------------------------------------------------

    def _get_browser_csrf_token(
        self,
        scanner_url: str,
    ) -> str:
        """
        Extract the CSRF token from the ACTIVE Playwright session.

        This token must belong to the same browser session used
        for /screener/process.
        """

        try:

            csrf_token = (
                self._page.locator(
                    'meta[name="csrf-token"]'
                ).get_attribute(
                    "content"
                )
            )

        except Exception as exc:

            raise RuntimeError(
                "CRITICAL: Failed to read active "
                "Playwright CSRF token: "
                f"{exc}"
            ) from exc

        if not csrf_token:

            raise RuntimeError(
                "CRITICAL: Active Playwright session "
                "does not expose a CSRF token: "
                f"{scanner_url}"
            )

        csrf_token = str(
            csrf_token
        ).strip()

        if not csrf_token:

            raise RuntimeError(
                "CRITICAL: Active Playwright CSRF token "
                "is empty: "
                f"{scanner_url}"
            )

        return csrf_token

    # ------------------------------------------------------------------
    # RUN SAVED SCAN
    # ------------------------------------------------------------------

    def run_saved_scan(
        self,
        halal_symbols: set,
        scanner_url: str,
    ) -> Tuple[
        List[TechnicalCandidate],
        Any,
        Dict[str, Any],
    ]:
        """
        Execute an account-owned Chartink saved scanner.

        Returns:

            candidates
            provenance
            meta_info
        """

        if not halal_symbols:

            raise RuntimeError(
                "CRITICAL INPUT FAILURE: "
                "canonical Halal universe is empty."
            )

        if LIVE_AUTO_EXECUTION:

            raise RuntimeError(
                "CRITICAL SAFETY BLOCK: "
                "LIVE_AUTO_EXECUTION must remain FALSE."
            )

        if not scanner_url.startswith(
            "https://chartink.com/screener/"
        ):

            raise ValueError(
                "Invalid Chartink scanner URL: "
                f"{scanner_url}"
            )

        # --------------------------------------------------------------
        # 1. Raw scanner HTML
        # --------------------------------------------------------------

        raw_html = (
            self._get_raw_scanner_html(
                scanner_url
            )
        )

        # --------------------------------------------------------------
        # 2. Exact atlas_query
        # --------------------------------------------------------------

        atlas_query = (
            self._extract_atlas_query(
                scanner_url,
                raw_html,
            )
        )

        # --------------------------------------------------------------
        # 3. Authenticated Playwright
        # --------------------------------------------------------------

        self.connect()

        logger.info(
            "Navigating authenticated Playwright session to: %s",
            scanner_url,
        )

        try:

            self._page.goto(
                scanner_url,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            self._page.wait_for_timeout(
                1000
            )

        except Exception as exc:

            raise RuntimeError(
                "Chartink scanner navigation failed: "
                f"{exc}"
            ) from exc

        # --------------------------------------------------------------
        # 4. Same-session CSRF
        # --------------------------------------------------------------

        csrf_token = (
            self._get_browser_csrf_token(
                scanner_url
            )
        )

        # --------------------------------------------------------------
        # 5. POST /screener/process
        # --------------------------------------------------------------

        logger.info(
            "Executing exact atlas_query through "
            "POST /screener/process..."
        )

        response_json = self._page.evaluate(
            """
            async (payload) => {

                const headers = {
                    "Content-Type":
                        "application/x-www-form-urlencoded; charset=UTF-8",

                    "X-Requested-With":
                        "XMLHttpRequest",

                    "Accept":
                        "application/json, text/javascript, */*; q=0.01",

                    "X-CSRF-TOKEN":
                        payload.csrfToken
                };

                let response;

                try {

                    response = await fetch(
                        "/screener/process",
                        {
                            method: "POST",
                            credentials: "include",
                            headers: headers,
                            body: new URLSearchParams({
                                "scan_clause":
                                    payload.scanClause
                            })
                        }
                    );

                } catch (fetchError) {

                    return {
                        transport_error:
                            String(fetchError),
                        status: null,
                        ok: false,
                        headers: {},
                        body: null,
                        raw_body: "",
                        json_parse_error: null
                    };
                }

                const responseText =
                    await response.text();

                const responseHeaders =
                    Object.fromEntries(
                        response.headers.entries()
                    );

                let parsed = null;
                let jsonParseError = null;

                try {

                    parsed = JSON.parse(
                        responseText
                    );

                } catch (parseError) {

                    jsonParseError =
                        String(parseError);
                }

                return {
                    status: response.status,
                    ok: response.ok,
                    headers: responseHeaders,
                    body: parsed,
                    raw_body:
                        responseText.substring(
                            0,
                            3000
                        ),
                    json_parse_error:
                        jsonParseError
                };
            }
            """,
            {
                "scanClause": atlas_query,
                "csrfToken": csrf_token,
            },
        )

        # --------------------------------------------------------------
        # 6. Validate response
        # --------------------------------------------------------------

        if not isinstance(
            response_json,
            dict,
        ):

            raise RuntimeError(
                "CRITICAL: Invalid Chartink "
                "process response."
            )

        transport_error = (
            response_json.get(
                "transport_error"
            )
        )

        if transport_error:

            raise RuntimeError(
                "CRITICAL: Chartink process "
                "transport error: "
                f"{transport_error}"
            )

        http_status = (
            response_json.get(
                "status"
            )
        )

        response_ok = (
            response_json.get(
                "ok"
            )
        )

        body = (
            response_json.get(
                "body"
            )
        )

        response_headers = (
            response_json.get(
                "headers",
                {},
            )
        )

        raw_body = (
            response_json.get(
                "raw_body",
                "",
            )
        )

        json_parse_error = (
            response_json.get(
                "json_parse_error"
            )
        )

        if (
            not response_ok
            or http_status != 200
        ):

            logger.error(
                "Chartink scanner process diagnostic | "
                "HTTP=%s | Headers=%s | Body=%s | "
                "JSONParseError=%s",
                http_status,
                response_headers,
                raw_body,
                json_parse_error,
            )

            raise RuntimeError(
                "CRITICAL: Chartink scanner process failed. "
                f"HTTP={http_status} | "
                f"Headers={response_headers} | "
                f"Body={raw_body} | "
                f"JSONParseError={json_parse_error}"
            )

        if not isinstance(
            body,
            dict,
        ):

            raise RuntimeError(
                "CRITICAL: Chartink process body "
                "is not JSON object."
            )

        # --------------------------------------------------------------
        # 7. Extract JSON scan results
        # --------------------------------------------------------------

        raw_data = body.get(
            "data",
            [],
        )

        if raw_data is None:
            raw_data = []

        if not isinstance(
            raw_data,
            list,
        ):

            raise RuntimeError(
                "CRITICAL: Chartink response "
                "'data' is not a list."
            )

        raw_count = len(
            raw_data
        )

        logger.info(
            "Chartink saved scan returned "
            "%s raw records.",
            raw_count,
        )

        # --------------------------------------------------------------
        # 8. Halal intersection
        # --------------------------------------------------------------

        normalized_halal_symbols = {
            str(symbol).upper().strip()
            for symbol in halal_symbols
            if str(symbol).strip()
        }

        candidates: List[
            TechnicalCandidate
        ] = []

        parsed_count = 0
        halal_match_count = 0

        for item in raw_data:

            if not isinstance(
                item,
                dict,
            ):
                continue

            parsed_count += 1

            symbol = str(
                item.get(
                    "nsecode",
                    "",
                )
            ).upper().strip()

            if not symbol:
                continue

            if (
                symbol
                not in normalized_halal_symbols
            ):
                continue

            halal_match_count += 1

            company_name = str(
                item.get(
                    "name",
                    symbol,
                )
            ).strip()

            try:

                close_price = float(
                    item.get(
                        "close",
                        0.0,
                    )
                )

            except (
                ValueError,
                TypeError,
            ):

                close_price = 0.0

            try:

                volume = int(
                    float(
                        item.get(
                            "volume",
                            0,
                        )
                    )
                )

            except (
                ValueError,
                TypeError,
            ):

                volume = 0

            try:

                per_change = float(
                    item.get(
                        "per_change",
                        0.0,
                    )
                )

            except (
                ValueError,
                TypeError,
            ):

                per_change = 0.0

            candidates.append(
                TechnicalCandidate(
                    symbol=symbol,
                    company_name=company_name,
                    close_price=close_price,
                    volume=volume,
                    per_change=per_change,
                    is_halal_confirmed=True,
                    has_execution_payload=False,
                )
            )

        # --------------------------------------------------------------
        # 9. Metadata
        # --------------------------------------------------------------

        meta_info = {
            "scanner_url": scanner_url,
            "transport": (
                "PLAYWRIGHT_AUTHENTICATED"
            ),
            "query_source": (
                "SCANNER_SCAN_JSON_ATLAS_QUERY"
            ),
            "csrf_source": (
                "ACTIVE_PLAYWRIGHT_SESSION"
            ),
            "raw_count": raw_count,
            "parsed_count": parsed_count,
            "halal_match_count": halal_match_count,
            "retained_count": len(
                candidates
            ),
            "canonical_halal_universe_size": len(
                normalized_halal_symbols
            ),
            "timestamp": time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

        self.provenance = (
            "LIVE_AUTHENTICATED_PLAYWRIGHT"
        )

        logger.info(
            "Chartink scan completed | "
            "Raw=%s | Parsed=%s | Halal=%s | "
            "Retained=%s",
            raw_count,
            parsed_count,
            halal_match_count,
            len(candidates),
        )

        return (
            candidates,
            self.provenance,
            meta_info,
        )