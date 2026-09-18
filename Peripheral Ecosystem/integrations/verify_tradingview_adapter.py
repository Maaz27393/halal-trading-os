from __future__ import annotations

import inspect
import sys
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\OBSIDIAN VAULT\halal-trading-os")
PERIPHERAL = ROOT / "Peripheral Ecosystem"
INTEGRATIONS = PERIPHERAL / "integrations"
SECURITY = PERIPHERAL / "operational_layer"

sys.path.insert(0, str(PERIPHERAL))
sys.path.insert(0, str(INTEGRATIONS))
sys.path.insert(0, str(SECURITY))


def model_to_dict(value: Any) -> dict[str, Any]:
    """Convert a Pydantic model or mapping into a normal dictionary."""
    if hasattr(value, "model_dump"):
        result = value.model_dump()
        if isinstance(result, dict):
            return result

    if hasattr(value, "dict"):
        result = value.dict()
        if isinstance(result, dict):
            return result

    if isinstance(value, dict):
        return value

    raise TypeError(
        f"Expected dict/Pydantic model, got {type(value).__name__}"
    )


def instantiate_adapter(adapter_cls):
    """Instantiate adapter while supporting common existing gateway signatures."""
    try:
        signature = inspect.signature(adapter_cls)
    except (TypeError, ValueError):
        signature = None

    # Try existing permission gateway first.
    try:
        from security.gateway import PermissionGateway
        gateway = PermissionGateway()
    except Exception:
        gateway = None

    if signature:
        parameters = signature.parameters

        if gateway is not None:
            if "gateway" in parameters:
                return adapter_cls(gateway=gateway)

            if "permission_gateway" in parameters:
                return adapter_cls(permission_gateway=gateway)

        required = [
            p for p in parameters.values()
            if p.name != "self"
            and p.default is inspect.Parameter.empty
            and p.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]

        if not required:
            return adapter_cls()

    # Final fallback.
    return adapter_cls()


def find_normalizer(adapter):
    """
    Locate the existing adapter method responsible for turning an
    incoming alert payload into the canonical representation.
    """
    candidates = [
        "normalize_signal",
        "normalize_alert",
        "to_canonical_signal",
        "parse_alert",
        "adapt_signal",
        "normalize",
        "adapt",
        "read",
    ]

    for name in candidates:
        method = getattr(adapter, name, None)
        if callable(method):
            return name, method

    raise AttributeError(
        "Could not find a signal normalization method on TradingViewAdapter. "
        f"Available public methods: "
        f"{[x for x in dir(adapter) if not x.startswith('_')]}"
    )


def main() -> int:
    print("=" * 72)
    print("TRADINGVIEW ADAPTER V1 REGRESSION TEST")
    print("=" * 72)

    try:
        from tradingview_adapter import TradingViewAdapter
    except Exception as exc:
        print(f"IMPORT: FAIL — {exc}")
        return 1

    print("IMPORT: PASS")
    print(f"Adapter class: {TradingViewAdapter.__name__}")

    try:
        signature = inspect.signature(TradingViewAdapter)
        print(f"Constructor: {signature}")
    except Exception:
        pass

    try:
        adapter = instantiate_adapter(TradingViewAdapter)
        print("INSTANTIATION: PASS")
    except Exception as exc:
        print(f"INSTANTIATION: FAIL — {exc}")
        return 1

    # ------------------------------------------------------------------
    # Governance & Capabilities verification (BaseConnector compliance)
    # ------------------------------------------------------------------
    print("\nGOVERNANCE & CAPABILITIES")
    try:
        caps = adapter.capabilities()
        print(f"Capabilities: {caps}")
        
        if "READ" in caps and "EXECUTE" not in caps:
            print("Capability Check: PASS (Read-only capabilities enforced)")
        else:
            print("Capability Check: FAIL — Unauthorized capabilities found")
            return 1
    except Exception as exc:
        print(f"GOVERNANCE & CAPABILITIES: FAIL — {exc}")
        return 1

    print("GOVERNANCE: PASS")

    # ------------------------------------------------------------------
    # Find normalization entry point & Contracts
    # ------------------------------------------------------------------
    try:
        method_name, normalizer = find_normalizer(adapter)
        print(f"\nNORMALIZER: {method_name}")
    except Exception as exc:
        print(f"NORMALIZER DISCOVERY: FAIL — {exc}")
        return 1

    try:
        from contracts import TradingSignal
    except Exception as exc:
        print(f"CONTRACTS IMPORT: FAIL — {exc}")
        return 1

   # ------------------------------------------------------------------
    # Test TradingView-style alert
    # ------------------------------------------------------------------
    payload = {
        "symbol": "NSE:INFY",
        "signal_type": "long_signal",
    }

    print("\nINPUT PAYLOAD")
    for key, value in payload.items():
        print(f"{key}: {value}")

    try:
        # Pass TradingSignal as target_model contract
        result = normalizer(payload, target_model=TradingSignal)
    except TypeError as exc:
        print(f"NORMALIZATION: FAIL — signature mismatch: {exc}")
        return 1
    except Exception as exc:
        print(f"NORMALIZATION: FAIL — {exc}")
        return 1

    try:
        canonical = model_to_dict(result)
    except Exception as exc:
        print(f"CANONICAL CONVERSION: FAIL — {exc}")
        return 1

    print("\nCANONICAL RESULT")
    for key, value in canonical.items():
        print(f"{key}: {value}")

    # ------------------------------------------------------------------
    # Explicit execution-surface check
    # ------------------------------------------------------------------
    forbidden = [
        "place_order",
        "modify_order",
        "cancel_order",
        "execute_order",
    ]

    exposed_forbidden = [
        name for name in forbidden if callable(getattr(adapter, name, None))
    ]

    if exposed_forbidden:
        print(
            "Execution surface: FAIL — "
            f"forbidden methods exposed: {exposed_forbidden}"
        )
        return 1
    else:
        print("Execution surface: PASS")

    print("\n" + "=" * 72)
    print("TRADINGVIEW ADAPTER V1 REGRESSION TEST: PASS")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())