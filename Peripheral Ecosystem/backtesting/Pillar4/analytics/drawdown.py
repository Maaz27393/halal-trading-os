"""
Portfolio Drawdown Engine (Pillar 4 - Phase C).
Computes chronological portfolio equity curves, running peaks, absolute drawdowns, 
percentage drawdowns, and maximum drawdown metrics.
"""
class DrawdownEngine:
    @staticmethod
    def compute_equity_curve(initial_capital: float, trades: list[dict]) -> dict:
        """
        Takes initial capital and a chronologically sorted list of trades containing net_pnl,
        and computes the equity curve, running peaks, drawdowns, and max drawdown statistics.
        """
        if not trades:
            return {
                "initial_capital": initial_capital,
                "final_equity": initial_capital,
                "max_drawdown_abs": 0.0,
                "max_drawdown_pct": 0.0,
                "equity_curve": []
            }

        current_equity = initial_capital
        peak_equity = initial_capital
        max_dd_abs = 0.0
        max_dd_pct = 0.0
        
        equity_points = []
        # Initial starting point
        equity_points.append({
            "timestamp": trades[0].get("entry_time", "START"),
            "equity": current_equity,
            "peak": peak_equity,
            "drawdown_abs": 0.0,
            "drawdown_pct": 0.0
        })

        for trade in trades:
            net_pnl = float(trade.get("net_pnl", 0.0))
            current_equity += net_pnl
            
            if current_equity > peak_equity:
                peak_equity = current_equity

            dd_abs = peak_equity - current_equity
            dd_pct = (dd_abs / peak_equity * 100.0) if peak_equity > 0 else 0.0

            if dd_abs > max_dd_abs:
                max_dd_abs = dd_abs
            if dd_pct > max_dd_pct:
                max_dd_pct = dd_pct

            equity_points.append({
                "timestamp": trade.get("exit_time", trade.get("entry_time")),
                "equity": round(current_equity, 2),
                "peak": round(peak_equity, 2),
                "drawdown_abs": round(dd_abs, 2),
                "drawdown_pct": round(dd_pct, 4)
            })

        return {
            "initial_capital": initial_capital,
            "final_equity": round(current_equity, 2),
            "max_drawdown_abs": round(max_dd_abs, 2),
            "max_drawdown_pct": round(max_dd_pct, 4),
            "equity_curve": equity_points
        }
