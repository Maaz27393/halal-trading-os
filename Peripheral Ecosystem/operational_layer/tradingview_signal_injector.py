import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Paths
BASE_DIR = Path(r"D:\OBSIDIAN VAULT\halal-trading-os")
OPERATIONAL_DIR = BASE_DIR / "Peripheral Ecosystem" / "operational_layer"
LOG_DIR = OPERATIONAL_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
SIGNAL_LOG = LOG_DIR / "tradingview_signals.log"

# Governance Invariants (Fail-Closed & Read-Only)
GOVERNANCE_CONFIG = {
    "read_only": True,
    "live_auto_execution": False,
    "order_capability": "NONE",
    "execution_authority": "NONE"
}

def inject_signal(ticker: str = "INFY", exchange: str = "NSE", close: str = "1545.50", action: str = "long_signal"):
    """
    Simulates a validated TradingView alert payload, normalizes it into a TradingSignal,
    and appends it to the auxiliary signal log to mirror Webhook Receiver V1 behavior.
    """
    print("=" * 70)
    print("HALAL TRADING OS - LOCAL TRADINGVIEW SIGNAL INJECTOR V1")
    print("Governance: READ_ONLY = True | ORDER_CAPABILITY = NONE")
    print("=" * 70)

    # 1. Build raw payload simulating TradingView placeholders
    raw_payload = {
        "ticker": ticker,
        "exchange": exchange,
        "close": close,
        "timenow": datetime.now(timezone.utc).isoformat(),
        "action": action
    }

    # 2. Wrap into normalized TradingSignal contract
    normalized_signal = {
        "governance": GOVERNANCE_CONFIG,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "raw_payload": raw_payload
    }

    # 3. Write to auxiliary signal store (matching receiver audit log format)
    log_entry = f'{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]} [INFO] Received Webhook Signal: {json.dumps(normalized_signal)}'
    
    with open(SIGNAL_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

    print(f"[1] Successfully injected mock signal for {exchange}:{ticker} into auxiliary store.")
    print(json.dumps(normalized_signal, indent=2))

    # 4. Automatically trigger downstream Orchestrator Adapter for regression testing
    adapter_path = OPERATIONAL_DIR / "tradingview_orchestrator_adapter.py"
    if adapter_path.exists():
        print("\n[2] Triggering downstream TradingView → Orchestrator Adapter...")
        result = subprocess.run(["python", str(adapter_path)], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("[STDERR]:", result.stderr)
    else:
        print(f"\n[WARNING] Orchestrator adapter not found at {adapter_path}")

if __name__ == "__main__":
    # Test injection with default INFY long signal
    inject_signal(ticker="INFY", exchange="NSE", close="1545.50", action="long_signal")