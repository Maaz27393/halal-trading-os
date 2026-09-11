from typing import Dict, Any, List

class PortfolioBacktester:
    """
    Phase 10D: Portfolio Backtester & Performance Analytics Engine
    Evaluates backtest trade logs and equity curves to compute statistical metrics:
    - Win Rate, Profit Factor, Expectancy
    - Peak-to-Trough Maximum Drawdown
    - Net Profit & Return on Capital
    """
    def calculate_metrics(self, equity_curve: List[Dict[str, Any]], trade_logs: List[Dict[str, Any]], initial_capital: float) -> Dict[str, Any]:
        if not equity_curve:
            return {"error": "Empty equity curve"}

        # Extract realized PnL per completed trade execution
        closed_pnls = []
        for log in trade_logs:
            exec_res = log.get("execution_result", {})
            realized = exec_res.get("realized_pnl", 0.0)
            if realized != 0.0:
                closed_pnls.append(realized)

        total_trades = len(closed_pnls)
        wins = [p for p in closed_pnls if p > 0]
        losses = [p for p in closed_pnls if p < 0]

        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / total_trades * 100.0) if total_trades > 0 else 0.0

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0.0)

        avg_win = (gross_profit / win_count) if win_count > 0 else 0.0
        avg_loss = (gross_loss / loss_count) if loss_count > 0 else 0.0

        win_prob = win_rate / 100.0
        loss_prob = (loss_count / total_trades) if total_trades > 0 else 0.0
        expectancy = (win_prob * avg_win) - (loss_prob * avg_loss)

        # Calculate Peak-to-Trough Maximum Drawdown from equity time-series
        peak_equity = initial_capital
        max_drawdown_pct = 0.0
        max_drawdown_amt = 0.0

        for entry in equity_curve:
            eq = entry["total_equity"]
            if eq > peak_equity:
                peak_equity = eq
            drawdown_amt = peak_equity - eq
            drawdown_pct = (drawdown_amt / peak_equity * 100.0) if peak_equity > 0 else 0.0

            if drawdown_pct > max_drawdown_pct:
                max_drawdown_pct = drawdown_pct
                max_drawdown_amt = drawdown_amt

        final_equity = equity_curve[-1]["total_equity"]
        net_profit = final_equity - initial_capital
        return_on_capital_pct = (net_profit / initial_capital * 100.0) if initial_capital > 0 else 0.0

        return {
            "initial_capital": round(initial_capital, 2),
            "final_equity": round(final_equity, 2),
            "net_profit": round(net_profit, 2),
            "return_on_capital_pct": round(return_on_capital_pct, 2),
            "total_trades": total_trades,
            "win_count": win_count,
            "loss_count": loss_count,
            "win_rate_pct": round(win_rate, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "expectancy_per_trade": round(expectancy, 2),
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "max_drawdown_amt": round(max_drawdown_amt, 2)
        }
