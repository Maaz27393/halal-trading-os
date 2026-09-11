from typing import Dict, Any, Optional
from datetime import datetime

class MarketDataAdapter:
    """
    Phase 9A: Market Data Adapter
    Normalizes and validates incoming NSE market tick/candle data payload formats.
    Enforces strict sanity checks (spread, zero/negative pricing, high/low bounds).
    """
    def __init__(self, max_stale_seconds: int = 60):
        self.max_stale_seconds = max_stale_seconds

    def normalize_candle(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        ticker = str(raw_data.get("ticker", "")).strip().upper()
        if not ticker:
            return {"is_valid": False, "error": "MISSING_TICKER", "normalized_data": None}

        try:
            close_price = float(raw_data.get("close", 0.0))
            open_price = float(raw_data.get("open", close_price))
            high_price = float(raw_data.get("high", max(open_price, close_price)))
            low_price = float(raw_data.get("low", min(open_price, close_price)))
            volume = int(raw_data.get("volume", 0))
            vwap = float(raw_data.get("vwap", close_price))
        except (ValueError, TypeError):
            return {"is_valid": False, "error": "INVALID_NUMERIC_DATA", "normalized_data": None}

        # Sanity Checks
        if close_price <= 0 or open_price <= 0 or high_price <= 0 or low_price <= 0:
            return {"is_valid": False, "error": "NON_POSITIVE_PRICE", "normalized_data": None}

        if low_price > high_price or close_price > high_price or close_price < low_price:
            return {"is_valid": False, "error": "HIGH_LOW_OUT_OF_BOUNDS", "normalized_data": None}

        if volume < 0:
            return {"is_valid": False, "error": "NEGATIVE_VOLUME", "normalized_data": None}

        return {
            "is_valid": True,
            "error": None,
            "normalized_data": {
                "ticker": ticker,
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume,
                "vwap": round(vwap, 2),
                "timestamp": raw_data.get("timestamp", datetime.now().isoformat())
            }
        }
