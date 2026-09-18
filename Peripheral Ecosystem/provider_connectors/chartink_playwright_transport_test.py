import sys
import json
import html
from pathlib import Path

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


def extract_query(page):
    content = page.content()
    soup = BeautifulSoup(content, "html.parser")
    scanner = soup.find("scanner")

    if not scanner:
        raise RuntimeError("No <scanner> element found.")

    raw = scanner.get(":scan-json")

    if not raw:
        raise RuntimeError("No :scan-json found.")

    data = json.loads(html.unescape(raw))

    query = data.get("atlas_query")

    if not query:
        raise RuntimeError("No atlas_query found.")

    return data, query


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    context = browser.new_context()

    cookies = ChartinkAuthSessionProvider().load_session_cookies()

    playwright_cookies = []

    for name, value in cookies.items():
        playwright_cookies.append({
            "name": name,
            "value": value,
            "domain": ".chartink.com",
            "path": "/"
        })

    context.add_cookies(playwright_cookies)

    page = context.new_page()

    for name, url in SCANNERS:

        print("\n" + "=" * 90)
        print(name)
        print(url)
        print("=" * 90)

        try:

            page.goto(
                url,
                wait_until="networkidle",
                timeout=30000
            )

            page.wait_for_timeout(1500)

            data, query = extract_query(page)

            print("Scanner ID:", data.get("id"))
            print("Scanner name:", data.get("name"))
            print("Query length:", len(query))
            print("Query extracted: YES")

            result = page.evaluate(
                """
                async (scanClause) => {

                    const csrfMeta =
                        document.querySelector(
                            'meta[name="csrf-token"]'
                        );

                    const csrfToken =
                        csrfMeta
                            ? csrfMeta.getAttribute("content")
                            : "";

                    const body =
                        new URLSearchParams();

                    body.append(
                        "scan_clause",
                        scanClause
                    );

                    const response =
                        await fetch(
                            "/screener/process",
                            {
                                method: "POST",
                                credentials: "same-origin",
                                headers: {
                                    "X-Requested-With":
                                        "XMLHttpRequest",
                                    "X-CSRF-TOKEN":
                                        csrfToken,
                                    "Accept":
                                        "application/json, text/javascript, */*; q=0.01"
                                },
                                body: body
                            }
                        );

                    const text =
                        await response.text();

                    return {
                        status: response.status,
                        csrf_present: !!csrfToken,
                        response_length: text.length,
                        response_text:
                            text.substring(0, 1000)
                    };
                }
                """,
                query
            )

            print("HTTP status:", result["status"])
            print(
                "CSRF token present:",
                result["csrf_present"]
            )
            print(
                "Response length:",
                result["response_length"]
            )

            if result["status"] == 200:

                try:
                    payload = json.loads(
                        result["response_text"]
                    )

                    print(
                        "Returned data:",
                        len(payload.get("data", []))
                    )

                except Exception:

                    print(
                        "Response preview:",
                        result["response_text"][:500]
                    )

            else:

                print(
                    "Response preview:",
                    result["response_text"][:500]
                )

        except Exception as exc:

            print(
                "ERROR:",
                type(exc).__name__,
                str(exc)
            )

    browser.close()

print("\nDIAGNOSTIC COMPLETE")
