import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


VAULT_ROOT = Path(
    r"D:\OBSIDIAN VAULT\halal-trading-os"
)

SESSION_FILE = (
    VAULT_ROOT
    / "Peripheral Ecosystem"
    / "Canonical Universe"
    / "chartink_session.json"
)

CHARTINK_URL = "https://chartink.com/"
SCANNER_URL = (
    "https://chartink.com/screener/"
    "vcp-smart-money-breakout-hunter"
)


def save_session_cookies(context):
    cookies = context.cookies(
        ["https://chartink.com/"]
    )

    if not cookies:
        raise RuntimeError(
            "No Chartink cookies were captured."
        )

    required = {
        cookie["name"]
        for cookie in cookies
    }

    if "XSRF-TOKEN" not in required:
        raise RuntimeError(
            "XSRF-TOKEN was not found in the "
            "refreshed Chartink session."
        )

    if "ci_session" not in required:
        raise RuntimeError(
            "ci_session was not found in the "
            "refreshed Chartink session."
        )

    SESSION_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        SESSION_FILE,
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            cookies,
            handle,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"Saved {len(cookies)} Chartink cookies to:"
    )
    print(SESSION_FILE)

    print("\nCookie names:")
    for name in sorted(required):
        print(f"  {name}")

    print("\nRequired cookies:")
    print(
        "  XSRF-TOKEN: PASS"
        if "XSRF-TOKEN" in required
        else "  XSRF-TOKEN: FAIL"
    )
    print(
        "  ci_session: PASS"
        if "ci_session" in required
        else "  ci_session: FAIL"
    )


def main():
    print("=" * 60)
    print("CHARTINK SESSION REFRESH")
    print("=" * 60)

    print("\nOpening a visible Chromium session...")
    print(
        "Log in to Chartink manually if required."
    )
    print(
        "Do not paste or provide credentials here."
    )

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=False
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        page.goto(
            CHARTINK_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print("\nBrowser opened.")
        print(
            f"Scanner test page: {SCANNER_URL}"
        )

        input(
            "\nAfter you are logged in and the "
            "Chartink page loads correctly, "
            "press ENTER here to capture the session..."
        )

        page.goto(
            SCANNER_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(2000)

        save_session_cookies(
            context
        )

        browser.close()

    print("\nSESSION REFRESH COMPLETE")


if __name__ == "__main__":
    main()