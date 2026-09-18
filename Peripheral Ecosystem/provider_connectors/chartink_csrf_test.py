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


SCANNERS = [
    (
        "Range Expansion",
        "https://chartink.com/screener/range-expansion"
    ),
    (
        "120-Day High",
        "https://chartink.com/screener/copy-120day-high-breakout-26093257"
    ),
    (
        "Institution Accumulation",
        "https://chartink.com/screener/institution-accumulation"
    ),
    (
        "Range Contraction Breakout",
        "https://chartink.com/screener/copy-ankur-s-breakout-scans-4680"
    ),
]


cookies = (
    ChartinkAuthSessionProvider()
    .load_session_cookies()
)

session = requests.Session()

session.headers.update({
    "User-Agent":
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
})

session.cookies.update(cookies)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    context = browser.new_context(
        user_agent=
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
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

    for scanner_name, scanner_url in SCANNERS:

        print("\n" + "=" * 90)
        print(scanner_name)
        print(scanner_url)
        print("=" * 90)

        try:

            # ------------------------------------------------------
            # 1. AUTHENTICATED HTTP PAGE
            # ------------------------------------------------------

            response = session.get(
                scanner_url,
                timeout=20
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
                raise RuntimeError(
                    "No <scanner> element."
                )

            raw_scan_json = scanner.get(
                ":scan-json"
            )

            if not raw_scan_json:
                raise RuntimeError(
                    "No :scan-json."
                )

            scanner_data = json.loads(
                html.unescape(raw_scan_json)
            )

            query = scanner_data.get(
                "atlas_query"
            )

            if not query:
                raise RuntimeError(
                    "No atlas_query."
                )

            # ------------------------------------------------------
            # 2. FIND CSRF TOKEN IN HTTP PAGE
            # ------------------------------------------------------

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

                csrf_input = soup.find(
                    "input",
                    {
                        "name": "_token"
                    }
                )

                if csrf_input:
                    csrf_token = (
                        csrf_input.get("value")
                        or ""
                    )

            print(
                "Scanner:",
                scanner_data.get("name")
            )

            print(
                "Scanner ID:",
                scanner_data.get("id")
            )

            print(
                "Query length:",
                len(query)
            )

            print(
                "HTTP CSRF token:",
                "FOUND"
                if csrf_token
                else "NOT FOUND"
            )

            # ------------------------------------------------------
            # 3. LOAD PAGE IN PLAYWRIGHT
            # ------------------------------------------------------

            page.goto(
                scanner_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(1000)

            print(
                "Browser URL:",
                page.url
            )

            # ------------------------------------------------------
            # 4. CHECK BROWSER CSRF TOKEN
            # ------------------------------------------------------

            browser_csrf = page.evaluate(
                """
                () => {
                    const meta =
                        document.querySelector(
                            'meta[name="csrf-token"]'
                        );

                    const input =
                        document.querySelector(
                            'input[name="_token"]'
                        );

                    return {
                        meta:
                            meta
                                ? meta.getAttribute("content")
                                : "",

                        input:
                            input
                                ? input.value
                                : ""
                    };
                }
                """
            )

            print(
                "Browser meta CSRF:",
                "FOUND"
                if browser_csrf["meta"]
                else "NOT FOUND"
            )

            print(
                "Browser input CSRF:",
                "FOUND"
                if browser_csrf["input"]
                else "NOT FOUND"
            )

            # ------------------------------------------------------
            # 5. SYNCHRONIZE HTTP CSRF TOKEN INTO BROWSER
            # ------------------------------------------------------

            if csrf_token:

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

            # ------------------------------------------------------
            # 6. EXECUTE EXACT SAVED QUERY
            # ------------------------------------------------------

            result = page.evaluate(
                """
                async ({scanClause, csrfToken}) => {

                    const headers = {
                        "Content-Type":
                            "application/x-www-form-urlencoded; charset=UTF-8",

                        "X-Requested-With":
                            "XMLHttpRequest",

                        "Accept":
                            "application/json, text/javascript, */*; q=0.01"
                    };

                    if (csrfToken) {
                        headers["X-CSRF-TOKEN"] =
                            csrfToken;
                    }

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

                        length:
                            text.length,

                        text:
                            text.substring(0, 2000)
                    };
                }
                """,
                {
                    "scanClause": query,
                    "csrfToken": csrf_token
                }
            )

            print(
                "Process status:",
                result["status"]
            )

            print(
                "Response length:",
                result["length"]
            )

            if result["status"] == 200:

                try:

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

                    if rows:
                        print(
                            "First symbol:",
                            rows[0].get(
                                "nsecode"
                            )
                            or rows[0].get(
                                "symbol"
                            )
                            or rows[0].get(
                                "name"
                            )
                        )

                except Exception as exc:

                    print(
                        "JSON parse error:",
                        exc
                    )

            else:

                print(
                    "Response:",
                    result["text"][:1000]
                )

        except Exception as exc:

            print(
                "ERROR:",
                type(exc).__name__,
                str(exc)
            )

    browser.close()

print("\nCSRF SYNCHRONIZATION DIAGNOSTIC COMPLETE")
