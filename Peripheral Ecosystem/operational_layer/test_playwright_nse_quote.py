import sys
import time

VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"
ECOSYSTEM_DIR = rf"{VAULT_ROOT}\Peripheral Ecosystem"
PROVIDER_DIR = rf"{ECOSYSTEM_DIR}\provider_connectors"

for path in [VAULT_ROOT, ECOSYSTEM_DIR, PROVIDER_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

def test_playwright_nse_quote(symbol: str = "RELIANCE"):
    print("=" * 60)
    print(f"PLAYWRIGHT (HTTP/1.1) NSE EQUITY QUOTE TEST: {symbol}")
    print("=" * 60)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright is not installed.")
        return

    with sync_playwright() as p:
        print("\n[1] Launching Chromium (disabling HTTP/2)...")
        # Disable HTTP/2 to prevent protocol mismatch errors on NSE edge servers
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-http2"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        target_url = f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}"
        print(f"[2] Navigating directly to {target_url}...")
        
        try:
            # Go directly to quote page with domcontentloaded to avoid waiting on heavy third-party tracking scripts
            page.goto(target_url, timeout=45000, wait_until="domcontentloaded")
            time.sleep(3)
        except Exception as e:
            print(f"Navigation warning: {e}")

        print("[3] Evaluating quote API response via browser context...")
        response_data = page.evaluate(f"""
            async () => {{
                try {{
                    const res = await fetch('https://www.nseindia.com/api/quote-equity?symbol={symbol}', {{
                        headers: {{
                            'Accept': 'application/json, text/plain, */*',
                            'X-Requested-With': 'XMLHttpRequest',
                            'Referer': 'https://www.nseindia.com/get-quotes/equity?symbol={symbol}'
                        }}
                    }});
                    if (res.ok) {{
                        return await res.json();
                    }}
                    return {{ error: 'HTTP status ' + res.status }};
                }} catch (err) {{
                    return {{ error: err.toString() }};
                }}
            }}
        """)

        print("\n[4] Diagnostic Result:")
        if isinstance(response_data, dict) and "error" in response_data:
            print(f"Fetch failed: {response_data['error']}")
        else:
            print("Successfully retrieved equity data via Playwright transport!")
            company_name = response_data.get("info", {}).get("companyName", "N/A")
            price_info = response_data.get("priceInfo", {}).get("lastPrice", "N/A")
            print(f"Company: {company_name}")
            print(f"Last Price: {price_info}")

        browser.close()

if __name__ == "__main__":
    test_playwright_nse_quote("RELIANCE")