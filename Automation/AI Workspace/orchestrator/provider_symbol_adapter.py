"""
Provider Symbol Adapter
-----------------------
Peripheral provider-mapping layer.

This module does NOT modify the frozen Phase 1-12 trading core.
"""

from __future__ import annotations

import re
from typing import Dict


# Diagnostic classifications
DATA_RECEIVED = "DATA_RECEIVED"
NSE_MAPPED_NS = "NSE_MAPPED_NS"
BSE_MAPPED_BO = "BSE_MAPPED_BO"
PROVIDER_SYMBOL_UNRESOLVED = "PROVIDER_SYMBOL_UNRESOLVED"
PROVIDER_DATA_UNAVAILABLE = "PROVIDER_DATA_UNAVAILABLE"
TEMPORARY_PROVIDER_ERROR = "TEMPORARY_PROVIDER_ERROR"
POTENTIAL_TICKER_CHANGE = "POTENTIAL_TICKER_CHANGE"
INVALID_CANONICAL_SYMBOL = "INVALID_CANONICAL_SYMBOL"


class ProviderSymbolAdapter:
    """
    Converts canonical symbols into provider-specific symbols.

    Canonical universe remains untouched.
    Provider-specific formatting is isolated here.
    """

    DEFAULT_ALIASES: Dict[str, str] = {
        "GVT&D": "GVT&D.NS",
        "M&M": "M&M.NS",
        "EMAMI_LTD": "EMAMILTD.NS",
        "IPCA_LABS": "IPCALAB.NS",
        "TIMEtechno": "TIMETECHNO.NS",
    }

    def __init__(self, aliases: Dict[str, str] | None = None):
        self.aliases = dict(self.DEFAULT_ALIASES)

        if aliases:
            self.aliases.update(aliases)

    @staticmethod
    def _clean_symbol(symbol) -> str:
        if symbol is None:
            return ""

        return re.sub(r"\s+", "", str(symbol).strip())

    @staticmethod
    def _is_numeric_bse(symbol: str) -> bool:
        return bool(re.fullmatch(r"\d{6}", symbol))

    def resolve(self, canonical_symbol) -> Dict[str, str | None]:
        """
        Resolve a canonical symbol.

        Returns a stable dictionary contract so the runner does not
        depend on provider-specific implementation details.
        """

        symbol = self._clean_symbol(canonical_symbol)

        if not symbol:
            return {
                "canonical_symbol": "",
                "provider_symbol": None,
                "exchange_type": None,
                "classification": INVALID_CANONICAL_SYMBOL,
                "reason": "Empty canonical symbol",
            }

        # Explicit aliases
        if symbol in self.aliases:
            provider_symbol = self.aliases[symbol]

            exchange = (
                "BSE"
                if provider_symbol.endswith(".BO")
                else "NSE"
            )

            return {
                "canonical_symbol": symbol,
                "provider_symbol": provider_symbol,
                "exchange_type": exchange,
                "classification": (
                    BSE_MAPPED_BO
                    if exchange == "BSE"
                    else NSE_MAPPED_NS
                ),
                "reason": "Explicit provider alias",
            }

        # Already qualified
        if symbol.endswith(".NS"):
            return {
                "canonical_symbol": symbol[:-3],
                "provider_symbol": symbol,
                "exchange_type": "NSE",
                "classification": NSE_MAPPED_NS,
                "reason": "Already NSE-qualified",
            }

        if symbol.endswith(".BO"):
            return {
                "canonical_symbol": symbol[:-3],
                "provider_symbol": symbol,
                "exchange_type": "BSE",
                "classification": BSE_MAPPED_BO,
                "reason": "Already BSE-qualified",
            }

        # Six-digit numeric scrip code = BSE
        if self._is_numeric_bse(symbol):
            return {
                "canonical_symbol": symbol,
                "provider_symbol": f"{symbol}.BO",
                "exchange_type": "BSE",
                "classification": BSE_MAPPED_BO,
                "reason": "Six-digit BSE scrip code",
            }

        # Standard NSE symbolic ticker
        if re.fullmatch(r"[A-Za-z0-9&._-]+", symbol):
            return {
                "canonical_symbol": symbol,
                "provider_symbol": f"{symbol}.NS",
                "exchange_type": "NSE",
                "classification": NSE_MAPPED_NS,
                "reason": "Standard NSE symbol mapping",
            }

        return {
            "canonical_symbol": symbol,
            "provider_symbol": None,
            "exchange_type": None,
            "classification": PROVIDER_SYMBOL_UNRESOLVED,
            "reason": "Unsupported symbol format",
        }


if __name__ == "__main__":
    adapter = ProviderSymbolAdapter()

    test_symbols = [
        "RELIANCE",
        "HEROMOTOCO",
        "GVT&D",
        "M&M",
        "543619",
        "506854",
        "543542",
    ]

    print("=" * 70)
    print("PROVIDER SYMBOL ADAPTER TEST")
    print("=" * 70)

    for symbol in test_symbols:
        print(symbol, "->", adapter.resolve(symbol))

    print("=" * 70)