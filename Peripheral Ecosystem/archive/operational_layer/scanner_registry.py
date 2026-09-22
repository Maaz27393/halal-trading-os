from typing import List, Dict, Any

# ==========================================
# M2: CHARTINK WATCHLIST REGISTRY
# ==========================================
WATCHLIST_REGISTRY = {
    "halal_stocks": {
        "name": "Halal Stocks",
        "enabled": True,
        "description": "Core canonical compliance-verified universe."
    },
    "breakout_confirmation": {
        "name": "Breakout Confirmation",
        "enabled": True,
        "description": "Watchlist for filtered candidates awaiting visual/intraday trigger."
    },
    "btst_swing": {
        "name": "BTST / Swing",
        "enabled": False,
        "description": "Short-term swing positioning universe."
    }
}

# ==========================================
# M1: SCANNER REGISTRY
# ==========================================
SCANNER_REGISTRY = [
    {
        "scanner_id": "range_expansion",
        "scanner_name": "Range Expansion",
        "mode": "STRUCTURAL",
        "timing": "PRE_MARKET",
        "input_watchlist": "Halal Stocks",
        "scanner_url": "https://chartink.com/screener/range-expansion", # Update with your exact Chartink URL/slug
        "halal_intersection": True,
        "enabled": True,
        "priority": 1,
        "output_type": "breakout_candidates"
    },
    {
        "scanner_id": "120_day_high",
        "scanner_name": "120-Day High",
        "mode": "STRUCTURAL",
        "timing": "PRE_MARKET",
        "input_watchlist": "Halal Stocks",
        "scanner_url": "https://chartink.com/screener/120-day-high", # Update with your exact Chartink URL/slug
        "halal_intersection": True,
        "enabled": True,
        "priority": 1,
        "output_type": "breakout_candidates"
    },
    {
        "scanner_id": "institution_accumulation",
        "scanner_name": "Institution Accumulation",
        "mode": "STRUCTURAL",
        "timing": "PRE_MARKET",
        "input_watchlist": "Halal Stocks",
        "scanner_url": "https://chartink.com/screener/institution-accumulation", # Update with your exact Chartink URL/slug
        "halal_intersection": True,
        "enabled": True,
        "priority": 1,
        "output_type": "breakout_candidates"
    },
    {
        "scanner_id": "range_contraction_breakout",
        "scanner_name": "Range Contraction Breakout (Ankur)",
        "mode": "STRUCTURAL",
        "timing": "PRE_MARKET",
        "input_watchlist": "Halal Stocks",
        "scanner_url": "https://chartink.com/screener/copy-ankur-s-breakout-scans-4680",
        "halal_intersection": True,
        "enabled": True,
        "priority": 1,
        "output_type": "breakout_candidates"
    },
    {
        "scanner_id": "breakout_confirmation_intraday",
        "scanner_name": "Breakout Confirmation",
        "mode": "INTRADAY",
        "timing": "MARKET_HOURS",
        "input_watchlist": "Breakout Confirmation",
        "scanner_url": "https://chartink.com/screener/breakout-confirmation", # Update URL as needed
        "halal_intersection": True,
        "enabled": True,
        "priority": 2,
        "output_type": "observation_candidates"
    },
    {
        "scanner_id": "rsi_above_60",
        "scanner_name": "RSI > 60 Momentum",
        "mode": "INTRADAY",
        "timing": "MARKET_HOURS",
        "input_watchlist": "Halal Stocks",
        "scanner_url": "https://chartink.com/screener/rsi-above-60", # Update URL as needed
        "halal_intersection": True,
        "enabled": True,
        "priority": 2,
        "output_type": "observation_candidates"
    }
]

def get_scanners_by_mode(mode: str) -> List[Dict[str, Any]]:
    """Retrieves all enabled scanners belonging to a specific operational mode."""
    return [s for s in SCANNER_REGISTRY if s["mode"] == mode and s["enabled"]]