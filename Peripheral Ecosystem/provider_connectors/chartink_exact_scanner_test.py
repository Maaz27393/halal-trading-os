import sys
import json
import html
import requests

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

sys.path.insert(
    0,
    r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem"
)

from provider_connectors.auth_session_provider import ChartinkAuthSessionProvider


TARGET_NAMES = [
    "RANGE EXPANSION -VOLUME SCAN",
    "120day high breakout",
    "Institution Accumulation",
    "RANGE CONTRACTION -BREAKOUT SCANS",
]


cookies = (
    ChartinkAuthSessionProvider()
    .load_session_cookies()
)

USER_AGENT = (
    "Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


session = requests.Session()

session.headers.update({
    "User-Agent": USER_AGENT
})

session.cookies.update(cookies)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    context = browser.new_context(
        user_agent=USER_AGENT
    )

    playwright_cookies = []

    for name, value in cookies.items():

        playwright_cookies.append({
            "name": name,
            "value": value,
            "domain": ".chartink.com",
            "path": "/"
        })

    context.add_cookies(
        playwright_cookies
    )

    page = context.new_page()

    print("=" * 100)
    print("CHARTINK EXACT ACCOUNT SCANNER DIAGNOSTIC")
    print("=" * 100)

    dashboard_url = "https://chartink.com/scan_dashboard"

    page.goto(
        dashboard_url,
        wait_until="domcontentloaded",
        timeout=30000
    )

    page.wait_for_timeout(2500)

    print("\nDashboard:")
    print(page.url)

    # ------------------------------------------------------------------
    # Extract scanner rows from the authenticated dashboard.
    # ------------------------------------------------------------------

    scanners = page.evaluate(
        """
        () => {

            const rows = [];

            const links =
                Array.from(
                    document.querySelectorAll(
                        'a[href*="/screener/"]'
                    )
                );

            for (const link of links) {

                const name =
                    (link.innerText || "")
                    .replace(/\\s+/g, " ")
                    .trim();

                const href =
                    link.href || "";

                if (!name || !href) {
                    continue;
                }

                rows.push({
                    name,
                    href
                });
            }

            return rows;
        }
        """
    )

    print("\nAccount-owned scanner links discovered:")

    for item in scanners:

        print(
            f"  {item['name']} -> {item['href']}"
        )

    # ------------------------------------------------------------------
    # Match requested scanners.
    # ------------------------------------------------------------------

    matched = {}

    for target in TARGET_NAMES:

        target_norm = (
            target
            .strip()
            .lower()
        )

        for item in scanners:

            name_norm = (
                item["name"]
                .strip()
                .lower()
            )

            if name_norm == target_norm:

                matched[target] = item
                break

    print("\n" + "=" * 100)
    print("EXACT ACCOUNT SCANNERS")
    print("=" * 100)

    for target in TARGET_NAMES:

        item = matched.get(target)

        if not item:

            print(
                f"\nNOT FOUND: {target}"
            )

        else:

            print(
                f"\n{target}"
            )

            print(
                "Actual name:",
                item["name"]
            )

            print(
                "Actual URL:",
                item["href"]
            )

    # ------------------------------------------------------------------
    # Execute exact saved queries.
    # ------------------------------------------------------------------

    for target in TARGET_NAMES:

        item = matched.get(target)

        if not item:
            continue

        scanner_name = item["name"]
        scanner_url = item["href"]

        print("\n" + "=" * 100)
        print(scanner_name)
        print(scanner_url)
        print("=" * 100)

        try:

            response = session.get(
                scanner_url,
                timeout=30
            )

            print(
                "HTTP page status:",
                response.status_code
            )

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            scanner = soup.find("scanner")

            if not scanner:

                print(
                    "ERROR: No <scanner> element"
                )

                continue

            raw_scan_json = scanner.get(
                ":scan-json"
            )

            if not raw_scan_json:

                print(
                    "ERROR: No :scan-json"
                )

                continue

            scanner_data = json.loads(
                html.unescape(
                    raw_scan_json
                )
            )

            query = scanner_data.get(
                "atlas_query"
            )

            print(
                "Scanner ID:",
                scanner_data.get("id")
            )

            print(
                "Scanner metadata name:",
                scanner_data.get("name")
            )

            print(
                "Query length:",
                len(query or "")
            )

            if not query:

                print(
                    "ERROR: No atlas_query"
                )

                continue

            print(
                "\nExact atlas_query:"
            )

            print(query)

            # ----------------------------------------------------------
            # CSRF token from exact scanner page.
            # ----------------------------------------------------------

            csrf_token = ""

            meta = soup.find(
                "meta",
                {
                    "name": "csrf-token"
                }
            )

            if meta:

                csrf_token = (
                    meta.get("content")
                    or ""
                )

            if not csrf_token:

                print(
                    "ERROR: CSRF token not found"
                )

                continue

            print(
                "\nHTTP CSRF token: FOUND"
            )

            # ----------------------------------------------------------
            # Browser loads exact scanner URL.
            # ----------------------------------------------------------

            page.goto(
                scanner_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(1000)

            # Synchronize CSRF token.
            page.evaluate(
                """
                (token) => {

                    let meta =
                        document.querySelector(
                            'meta[name="csrf-token"]'
                        );

                    if (!meta) {

                        meta =
                            document.createElement(
                                'meta'
                            );

                        meta.setAttribute(
                            'name',
                            'csrf-token'
                        );

                        document.head.appendChild(
                            meta
                        );
                    }

                    meta.setAttribute(
                        'content',
                        token
                    );
                }
                """,
                csrf_token
            )

            # ----------------------------------------------------------
            # Execute exact saved query.
            # ----------------------------------------------------------

            result = page.evaluate(
                """
                async ({scanClause, csrfToken}) => {

                    const headers = {

                        "Content-Type":
                            "application/x-www-form-urlencoded; charset=UTF-8",

                        "X-Requested-With":
                            "XMLHttpRequest",

                        "Accept":
                            "application/json, text/javascript, */*; q=0.01",

                        "X-CSRF-TOKEN":
                            csrfToken
                    };

                    const response =
                        await fetch(
                            "/screener/process",
                            {
                                method: "POST",

                                credentials: "include",

                                headers: headers,

                                body:
                                    new URLSearchParams({
                                        "scan_clause":
                                            scanClause
                                    })
                            }
                        );

                    const text =
                        await response.text();

                    return {
                        status:
                            response.status,

                        text:
                            text
                    };
                }
                """,
                {
                    "scanClause": query,
                    "csrfToken": csrf_token
                }
            )

            print(
                "\nProcess status:",
                result["status"]
            )

            if result["status"] != 200:

                print(
                    "ERROR response:",
                    result["text"][:2000]
                )

                continue

            payload = json.loads(
                result["text"]
            )

            rows = payload.get(
                "data",
                []
            )

            print(
                "Returned rows:",
                len(rows)
            )

            symbols = []

            for row in rows:

                symbol = (
                    row.get("nsecode")
                    or row.get("symbol")
                    or ""
                )

                symbol = (
                    str(symbol)
                    .upper()
                    .strip()
                )

                if symbol:

                    symbols.append(
                        symbol
                    )

            print(
                "Returned symbols:"
            )

            if symbols:

                print(
                    ", ".join(symbols)
                )

            else:

                print(
                    "(none)"
                )

            # ----------------------------------------------------------
            # Manual expected baseline.
            # ----------------------------------------------------------

            expected = {
                "RANGE EXPANSION -VOLUME SCAN": 0,
                "120day high breakout": 0,
                "Institution Accumulation": 2,
                "RANGE CONTRACTION -BREAKOUT SCANS": 4,
            }

            expected_count = None

            for key, value in expected.items():

                if (
                    key.lower()
                    ==
                    scanner_name.lower()
                ):

                    expected_count = value
                    break

            if expected_count is not None:

                actual_count = len(symbols)

                print(
                    "\nManual expected:",
                    expected_count
                )

                print(
                    "Automated result:",
                    actual_count
                )

                if actual_count == expected_count:

                    print(
                        "STATUS: MATCH"
                    )

                else:

                    print(
                        "STATUS: MISMATCH"
                    )

        except Exception as exc:

            print(
                "\nERROR:",
                type(exc).__name__,
                str(exc)
            )

    browser.close()

print("\n" + "=" * 100)
print("EXACT ACCOUNT SCANNER DIAGNOSTIC COMPLETE")
print("=" * 100)
