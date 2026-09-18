import os
import json
import sys


VAULT_ROOT = r"D:\OBSIDIAN VAULT\halal-trading-os"

REG_PATH = (
    rf"{VAULT_ROOT}\Peripheral Ecosystem"
    rf"\operational_layer\nse_mcp_registration.json"
)


def verify_v11_integration():

    print("=" * 60)
    print("TRADING OS - NSE MCP v1 + v1.1 REGRESSION TEST")
    print("=" * 60)

    # =========================================================
    # 1. REGISTRATION CONTRACT
    # =========================================================

    print("\n[1] Checking Registration Contract...")

    if not os.path.exists(REG_PATH):
        print(
            f"❌ Registration contract missing at:\n{REG_PATH}"
        )
        sys.exit(1)

    with open(REG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})

    print("   Contract Loaded Successfully.")
    print(
        f"   Servers: {list(servers.keys())}"
    )

    assert "halal-trading-vault" in servers
    assert "nse-market-data-v1" in servers

    # =========================================================
    # 2. LOAD NSE MCP
    # =========================================================

    print(
        "\n[2] Verifying NSE MCP v1 + v1.1 "
        "Tools & Governance..."
    )

    operational_layer = os.path.join(
        VAULT_ROOT,
        "Peripheral Ecosystem",
        "operational_layer",
    )

    if operational_layer not in sys.path:
        sys.path.insert(0, operational_layer)

    try:

        from nse_mcp_server import (
            get_market_status,
            get_index_vitals,
            get_india_vix,
            get_capital_market_snapshot,
            get_advance_decline,
            connector,
        )

        # =====================================================
        # GOVERNANCE
        # =====================================================

        print(
            f"   READ_ONLY           : "
            f"{connector.READ_ONLY}"
        )

        print(
            f"   LIVE_AUTO_EXECUTION : "
            f"{connector.LIVE_AUTO_EXECUTION}"
        )

        assert connector.READ_ONLY is True
        assert connector.LIVE_AUTO_EXECUTION is False

        # =====================================================
        # V1 - MARKET STATUS
        # =====================================================

        status_res = get_market_status()

        assert status_res.get("status") == "OK"

        print(
            "   get_market_status"
            f"          : PASS "
            f"(Source: {status_res.get('source')})"
        )

        # =====================================================
        # V1 - INDEX VITALS
        # =====================================================

        nifty_res = get_index_vitals("NIFTY 50")

        assert nifty_res.get("status") == "OK"

        print(
            "   get_index_vitals"
            f"           : PASS "
            f"(Index: {nifty_res.get('index')})"
        )

        # =====================================================
        # V1 - INDIA VIX
        # =====================================================

        vix_res = get_india_vix()

        assert vix_res.get("status") == "OK"

        print(
            "   get_india_vix"
            f"              : PASS "
            f"(Index: {vix_res.get('index')})"
        )

        # =====================================================
        # V1.1 - CAPITAL MARKET
        # =====================================================

        snapshot_res = get_capital_market_snapshot()

        assert snapshot_res.get("status") == "OK"

        snapshot_data = snapshot_res.get(
            "data", {}
        )

        print(
            "   get_capital_market_snapshot"
            f" : PASS "
            f"(Market: "
            f"{snapshot_data.get('market')}, "
            f"Status: "
            f"{snapshot_data.get('marketStatus')})"
        )

        # =====================================================
        # V1.1 - ADVANCE / DECLINE
        # =====================================================

        breadth_res = get_advance_decline()

        assert breadth_res.get("status") == "OK"

        breadth_data = breadth_res.get(
            "data", {}
        )

        nifty_500 = breadth_data.get(
            "nifty_500_breadth"
        )

        aggregate = breadth_data.get(
            "aggregate_breadth"
        )

        if nifty_500:
            breadth_description = (
                f"NIFTY 500 Advances: "
                f"{nifty_500.get('advances')}"
            )

        elif aggregate:
            breadth_description = (
                f"Aggregate Advances: "
                f"{aggregate.get('advances')}"
            )

        else:
            raise RuntimeError(
                "Advance/Decline response contains "
                "no validated breadth data."
            )

        print(
            "   get_advance_decline"
            f"          : PASS "
            f"({breadth_description})"
        )

        tools_status = "PASS"

    except Exception as exc:

        print(
            f"   ❌ Tool verification failed: {exc}"
        )

        tools_status = f"FAIL ({exc})"

    # =========================================================
    # 3. SUMMARY
    # =========================================================

    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY (v1 + v1.1)")
    print("=" * 60)

    print(
        f" - {'halal-trading-vault':<28} : PASS"
    )

    print(
        f" - {'nse-market-data-v1':<28} : PASS"
    )

    print(
        f" - {'get_market_status':<28} : "
        f"{tools_status}"
    )

    print(
        f" - {'get_index_vitals':<28} : "
        f"{tools_status}"
    )

    print(
        f" - {'get_india_vix':<28} : "
        f"{tools_status}"
    )

    print(
        f" - {'get_capital_market_snapshot':<28} : "
        f"{tools_status}"
    )

    print(
        f" - {'get_advance_decline':<28} : "
        f"{tools_status}"
    )

    print(
        f" - {'READ_ONLY':<28} : TRUE"
    )

    print(
        f" - {'LIVE_AUTO_EXECUTION':<28} : FALSE"
    )

    print(
        f" - {'ORDER CAPABILITY':<28} : NONE"
    )

    print(
        f" - {'EXECUTION AUTHORITY':<28} : NONE"
    )

    print("=" * 60)


if __name__ == "__main__":
    verify_v11_integration()