import os
import sys
import time
from bs4 import BeautifulSoup

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"

if VAULT_ROOT not in sys.path:
    sys.path.insert(0, VAULT_ROOT)

ECOSYSTEM_DIR = os.path.join(VAULT_ROOT, "Peripheral Ecosystem")
PROVIDER_DIR = os.path.join(ECOSYSTEM_DIR, "provider_connectors")

if ECOSYSTEM_DIR not in sys.path:
    sys.path.insert(0, ECOSYSTEM_DIR)

if PROVIDER_DIR not in sys.path:
    sys.path.insert(0, PROVIDER_DIR)

from provider_connectors.auth_session_provider import ChartinkAuthSessionProvider


def discover_all_scanners():

    print("=" * 60)
    print("CHARTINK ACCOUNT SCANNER DISCOVERY")
    print("=" * 60)

    auth_provider = ChartinkAuthSessionProvider()
    session_cookies = auth_provider.load_session_cookies()

    if not session_cookies:
        raise RuntimeError(
            "No authenticated Chartink session cookies found."
        )

    print(
        f"Authenticated session loaded: "
        f"{len(session_cookies)} cookie(s)"
    )

    from playwright.sync_api import sync_playwright

    scanners_found = {}

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        context = browser.new_context()

        cookie_list = []

        for name, value in session_cookies.items():
            if value is None:
                continue

            cookie_list.append(
                {
                    "name": str(name),
                    "value": str(value),
                    "domain": ".chartink.com",
                    "path": "/",
                }
            )

        context.add_cookies(cookie_list)

        page = context.new_page()

        dashboard_url = "https://chartink.com/scan_dashboard"

        print(f"\nOpening: {dashboard_url}")

        page.goto(
            dashboard_url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(3000)

        def extract_current_page():

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            found = 0

            for link in soup.find_all("a", href=True):

                href = link.get("href", "").strip()

                if "/screener/" not in href:
                    continue

                name = link.get_text(
                    " ",
                    strip=True
                )

                if not name:
                    continue

                full_url = (
                    href
                    if href.startswith("http")
                    else "https://chartink.com" + href
                )

                if full_url not in scanners_found.values():

                    scanners_found[name] = full_url
                    found += 1

            return found

        # ----------------------------------------------------------
        # PAGE 1
        # ----------------------------------------------------------

        print("\nScanning dashboard page 1...")

        found = extract_current_page()

        print(f"Scanners found on page 1: {found}")

        # ----------------------------------------------------------
        # PAGE 2
        # ----------------------------------------------------------

        page_two_found = False

        try:

            page_two = page.locator(
                "a",
                has_text="2"
            ).first

            if page_two.count() > 0:

                print("\nPagination detected.")

                page_two.click()

                page.wait_for_timeout(2500)

                found = extract_current_page()

                print(
                    f"Scanners found on page 2: {found}"
                )

                page_two_found = True

        except Exception as e:

            print(
                f"Page 2 navigation attempt failed: {e}"
            )

        # ----------------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------------

        print("\n" + "=" * 60)
        print(
            f"TOTAL UNIQUE ACCOUNT SCANNERS: "
            f"{len(scanners_found)}"
        )
        print("=" * 60)

        for index, (name, url) in enumerate(
            scanners_found.items(),
            start=1
        ):

            print(f"{index}. {name}")
            print(f"   {url}")
            print()

        print("=" * 60)

        if len(scanners_found) == 14:

            print(
                "SUCCESS: All 14 account-owned scanners discovered."
            )

        else:

            print(
                f"WARNING: Expected 14 scanners, "
                f"but discovered {len(scanners_found)}."
            )

            if not page_two_found:
                print(
                    "Page 2 was not successfully processed."
                )

        print("=" * 60)

        browser.close()


if __name__ == "__main__":
    discover_all_scanners()