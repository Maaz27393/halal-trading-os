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


def get_saved_query(session, url):

    response = session.get(
        url,
        timeout=20
    )

    print("HTTP page status:", response.status_code)

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    scanner = soup.find("scanner")

    if not scanner:
        raise RuntimeError(
            "HTTP page did not contain <scanner>."
        )

    raw = scanner.get(":scan-json")

    if not raw:
        raise RuntimeError(
            "HTTP page did not contain :scan-json."
        )

    data = json.loads(
        html.unescape(raw)
    )

    query = data.get("atlas_query")

    if not query:
        raise RuntimeError(
            "Scanner contains no atlas_query."
        )

    return data, query


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

            data, query = get_saved_query(
                session,
                scanner_url
            )

            print(
                "Scanner:",
                data.get("name")
            )

            print(
                "Scanner ID:",
                data.get("id")
            )

            print(
                "Query length:",
                len(query)
            )

            # ------------------------------------------------------
            # Load authenticated browser page first
            # ------------------------------------------------------

            page.goto(
                scanner_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            page.wait_for_timeout(1500)

            print(
                "Browser URL:",
                page.url
            )

            # ------------------------------------------------------
            # Execute exact saved query inside browser context
            # ------------------------------------------------------

            result = page.evaluate(
                """
                async (scanClause) => {

                    const response =
                        await fetch(
                            "/screener/process",
                            {
                                method: "POST",
                                credentials: "include",
                                headers: {
                                    "Content-Type":
                                        "application/x-www-form-urlencoded; charset=UTF-8",
                                    "X-Requested-With":
                                        "XMLHttpRequest",
                                    "Accept":
                                        "application/json, text/javascript, */*; q=0.01"
                                },
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

                        url:
                            response.url,

                        length:
                            text.length,

                        text:
                            text.substring(0, 2000)
                    };
                }
                """,
                query
            )

            print(
                "Process status:",
                result["status"]
            )

            print(
                "Process URL:",
                result["url"]
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
                            "First row:",
                            rows[0]
                        )

                except Exception as exc:

                    print(
                        "JSON parse error:",
                        exc
                    )

                    print(
                        "Response:",
                        result["text"][:500]
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

print("\nDIAGNOSTIC COMPLETE")
