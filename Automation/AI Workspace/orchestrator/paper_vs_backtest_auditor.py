from typing import Dict, Any, List

class PaperVsBacktestAuditor:
    """
    Phase 10F: Paper-vs-Backtest Consistency Auditor
    Audits execution outputs from the Paper Trading Engine and Historical Backtest Engine
    to detect logic drift, price discrepancies, or state divergence.
    """
    def __init__(self, tolerance_pct: float = 0.01):
        self.tolerance_pct = tolerance_pct

    def audit_runs(self, paper_result: Dict[str, Any], backtest_result: Dict[str, Any]) -> Dict[str, Any]:
        drifts = []

        # 1. Compare trade counts
        paper_trades = paper_result.get("executed_trades", 0)
        backtest_trades = backtest_result.get("executed_trades", 0)
        if paper_trades != backtest_trades:
            drifts.append(f"Trade count mismatch: Paper={paper_trades}, Backtest={backtest_trades}")

        # 2. Compare final total equity
        paper_equity = paper_result.get("final_portfolio", {}).get("total_equity", 0.0)
        backtest_equity = backtest_result.get("final_portfolio", {}).get("total_equity", 0.0)
        equity_diff = abs(paper_equity - backtest_equity)
        max_allowed_diff = paper_equity * (self.tolerance_pct / 100.0)

        if equity_diff > max_allowed_diff:
            drifts.append(f"Equity drift exceeded limit: Paper={paper_equity}, Backtest={backtest_equity}, Diff={equity_diff}")

        # 3. Compare open positions
        paper_positions = paper_result.get("final_portfolio", {}).get("open_positions_count", 0)
        backtest_positions = backtest_result.get("final_portfolio", {}).get("open_positions_count", 0)
        if paper_positions != backtest_positions:
            drifts.append(f"Open positions count mismatch: Paper={paper_positions}, Backtest={backtest_positions}")

        # 4. Compare realized PnL
        paper_realized = paper_result.get("final_portfolio", {}).get("total_realized_pnl", 0.0)
        backtest_realized = backtest_result.get("final_portfolio", {}).get("total_realized_pnl", 0.0)
        if abs(paper_realized - backtest_realized) > 0.05:
            drifts.append(f"Realized PnL mismatch: Paper={paper_realized}, Backtest={backtest_realized}")

        parity_passed = len(drifts) == 0

        return {
            "parity_passed": parity_passed,
            "drift_count": len(drifts),
            "drifts": drifts,
            "audit_summary": "ZERO_DRIFT_VERIFIED" if parity_passed else "DRIFT_DETECTED"
        }
