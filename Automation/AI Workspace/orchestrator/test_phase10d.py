import sys
from pathlib import Path

workspace_path = Path(__file__).parent.parent
sys.path.extend([
    str(Path(__file__).parent),
    str(workspace_path / "Agent Runtime"),
    str(workspace_path / "Agent Runtime" / "skills")
])

from portfolio_backtester import PortfolioBacktester

def run_phase10d_tests():
    print("=== STARTING PHASE 10D: PORTFOLIO BACKTESTER TESTS ===")
    tester = PortfolioBacktester()

    initial_capital = 200000.0

    # Mock Equity Curve with a peak and pullback (Drawdown test)
    equity_curve = [
        {"total_equity": 200000.0},
        {"total_equity": 210000.0}, # Peak 1
        {"total_equity": 205000.0}, # Drawdown: 5,000 / 210,000 = 2.38%
        {"total_equity": 220000.0}, # Peak 2
        {"total_equity": 209000.0}, # Peak 2 Drawdown: 11,000 / 220,000 = 5.0%
        {"total_equity": 225000.0}  # Final Equity
    ]

    # Mock Trade Logs with 3 wins (+3000, +5000, +7000) and 1 loss (-2500)
    trade_logs = [
        {"execution_result": {"realized_pnl": 3000.0}},
        {"execution_result": {"realized_pnl": 5000.0}},
        {"execution_result": {"realized_pnl": -2500.0}},
        {"execution_result": {"realized_pnl": 7000.0}}
    ]

    metrics = tester.calculate_metrics(equity_curve, trade_logs, initial_capital)

    # Test 1: Trade Count & Win Rate Calculation
    assert metrics["total_trades"] == 4
    assert metrics["win_count"] == 3
    assert metrics["loss_count"] == 1
    assert metrics["win_rate_pct"] == 75.0
    print("[PASS] Test 1 | Trade Count & Win Rate Analytics Verified")

    # Test 2: Profit Factor & Expectancy Calculation
    # Gross Profit = 15000, Gross Loss = 2500 -> Profit Factor = 6.0
    assert metrics["gross_profit"] == 15000.0
    assert metrics["gross_loss"] == 2500.0
    assert metrics["profit_factor"] == 6.0
    assert metrics["expectancy_per_trade"] == 3125.0 # (0.75 * 5000) - (0.25 * 2500)
    print("[PASS] Test 2 | Profit Factor & Trade Expectancy Verified")

    # Test 3: Maximum Drawdown & Equity Return Metrics
    assert metrics["net_profit"] == 25000.0
    assert metrics["return_on_capital_pct"] == 12.5
    assert metrics["max_drawdown_pct"] == 5.0 # Max drop occurred at Peak 2 (220k -> 209k)
    assert metrics["max_drawdown_amt"] == 11000.0
    print("[PASS] Test 3 | Max Drawdown & Net Return Calculations Verified")

    print("\nPhase 10D Portfolio Backtester Benchmark: 3/3 Passed")

if __name__ == "__main__":
    run_phase10d_tests()
