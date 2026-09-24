"""
Trade Attribution Module (Pillar 4 - Phase C).
Consumes certified parity trade results read-only and computes deterministic derived 
performance metrics (R-multiple, outcomes, exit classifications, and trade duration).
"""
import copy
from datetime import datetime

class TradeAttributionEngine:
    @staticmethod
    def enrich_trades(certified_trades: list[dict]) -> list[dict]:
        """
        Consumes a list of certified trade dicts, preserving all original fields 
        while adding deterministic derived analytical fields.
        Guarantees zero mutation of input objects.
        """
        if not certified_trades:
            return []

        enriched = []
        for trade in certified_trades:
            # Deepcopy to ensure absolute immutability of original certified records
            item = copy.deepcopy(trade)

            net_pnl = float(item.get("net_pnl", 0.0))
            entry_price = float(item.get("entry_price", 0.0))
            stop_loss = float(item.get("stop_loss", entry_price))
            direction = str(item.get("direction", "BUY")).upper()

            # 1. Determine initial risk per unit / trade
            # Risk = absolute distance between entry price and stop loss
            if direction == "BUY":
                risk_per_unit = entry_price - stop_loss
            else:
                risk_per_unit = stop_loss - entry_price

            # Handle zero or negative/invalid initial risk safely
            if risk_per_unit <= 0:
                item["initial_risk"] = 0.0
                item["r_multiple"] = 0.0
                item["risk_status"] = "INVALID_OR_ZERO_RISK"
            else:
                item["initial_risk"] = risk_per_unit
                # R-multiple = Net P&L / Initial Risk (normalized per unit or total capital risk)
                # Assuming unit quantity sizing or direct cash risk mapping:
                qty = float(item.get("quantity", 1.0))
                total_risk = risk_per_unit * qty
                if total_risk > 0:
                    item["r_multiple"] = round(net_pnl / total_risk, 4)
                else:
                    item["r_multiple"] = 0.0
                item["risk_status"] = "VALID"

            # 2. Outcome tags
            if net_pnl > 0:
                item["outcome"] = "WIN"
                item["is_winner"] = True
                item["is_loser"] = False
            elif net_pnl < 0:
                item["outcome"] = "LOSS"
                item["is_winner"] = False
                item["is_loser"] = True
            else:
                item["outcome"] = "BREAKEVEN"
                item["is_winner"] = False
                item["is_loser"] = False

            # 3. Exit classification
            reason = str(item.get("reason", "UNKNOWN")).upper()
            if "STOP" in reason:
                item["exit_classification"] = "STOP_LOSS_HIT"
            elif "PROFIT" in reason or "TARGET" in reason:
                item["exit_classification"] = "TAKE_PROFIT_HIT"
            else:
                item["exit_classification"] = "MANUAL_OR_SIGNAL_EXIT"

            # 4. Trade duration calculation
            entry_time_raw = item.get("entry_time")
            exit_time_raw = item.get("exit_time")
            
            if isinstance(entry_time_raw, str):
                entry_dt = datetime.strptime(entry_time_raw, "%Y-%m-%d %H:%M:%S")
            else:
                entry_dt = entry_time_raw

            if isinstance(exit_time_raw, str):
                exit_dt = datetime.strptime(exit_time_raw, "%Y-%m-%d %H:%M:%S")
            else:
                exit_dt = exit_time_raw

            if entry_dt and exit_dt:
                duration_delta = exit_dt - entry_dt
                item["trade_duration_seconds"] = int(duration_delta.total_seconds())
                item["trade_duration_minutes"] = round(duration_delta.total_seconds() / 60.0, 2)
            else:
                item["trade_duration_seconds"] = 0
                item["trade_duration_minutes"] = 0.0

            enriched.append(item)

        return enriched
