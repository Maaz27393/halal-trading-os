"""
Trade Metrics Module (Pillar 4 - MAE & MFE).
Calculates Maximum Adverse Excursion (MAE) and Maximum Favorable Excursion (MFE) 
using historical intrabar price series over the trade lifecycle.
"""
from datetime import datetime

class TradeMetricsEngine:
    @staticmethod
    def calculate_excursions(trade: dict, historical_bars: list) -> dict:
        """
        Calculates absolute and percentage MAE and MFE for a given trade 
        based on intrabar High and Low prices between entry_time and exit_time.
        """
        entry_time_raw = trade.get("entry_time")
        exit_time_raw = trade.get("exit_time")
        entry_price = float(trade.get("entry_price", 0.0))
        direction = str(trade.get("direction", "BUY")).upper()

        if isinstance(entry_time_raw, str):
            entry_dt = datetime.strptime(entry_time_raw, "%Y-%m-%d %H:%M:%S")
        else:
            entry_dt = entry_time_raw

        if isinstance(exit_time_raw, str):
            exit_dt = datetime.strptime(exit_time_raw, "%Y-%m-%d %H:%M:%S")
        else:
            exit_dt = exit_time_raw

        # Filter bars active during trade lifecycle [entry_dt, exit_dt]
        active_bars = [
            b for b in historical_bars 
            if entry_dt <= b.timestamp <= exit_dt
        ]

        if not active_bars or entry_price <= 0:
            return {
                "mae_abs": 0.0,
                "mae_pct": 0.0,
                "mfe_abs": 0.0,
                "mfe_pct": 0.0
            }

        if direction == "BUY":
            # MAE for BUY = Lowest price reached below entry (worst adverse)
            lowest_price = min(b.low for b in active_bars)
            mae_abs = max(0.0, entry_price - lowest_price)
            
            # MFE for BUY = Highest price reached above entry (best favorable)
            highest_price = max(b.high for b in active_bars)
            mfe_abs = max(0.0, highest_price - entry_price)
        else:
            # MAE for SHORT = Highest price reached above entry
            highest_price = max(b.high for b in active_bars)
            mae_abs = max(0.0, highest_price - entry_price)
            
            # MFE for SHORT = Lowest price reached below entry
            lowest_price = min(b.low for b in active_bars)
            mfe_abs = max(0.0, entry_price - lowest_price)

        mae_pct = round((mae_abs / entry_price) * 100.0, 4) if entry_price > 0 else 0.0
        mfe_pct = round((mfe_abs / entry_price) * 100.0, 4) if entry_price > 0 else 0.0

        return {
            "mae_abs": round(mae_abs, 4),
            "mae_pct": mae_pct,
            "mfe_abs": round(mfe_abs, 4),
            "mfe_pct": mfe_pct
        }
