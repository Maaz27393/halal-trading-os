import logging
import json
from typing import List, Dict, Any
from backtesting.contracts.backtest_contract import BacktestReport

logger = logging.getLogger("PowerBIAnalyticsExporter")

class OpportunityLifecyclePowerBIExporter:
    """
    Transforms backtest reports and trade simulations into flattened, 
    Power BI-optimized tabular payloads (15A — Opportunity Lifecycle Analytics).
    Strictly read-only / non-execution.
    """
    def __init__(self):
        self.live_auto_execution = False

    def export_lifecycle_to_table(self, reports: List[BacktestReport]) -> List[Dict[str, Any]]:
        """
        Flattens multi-stage trade results and lifecycle metrics into a tabular format 
        ready for direct CSV/Parquet import into Power BI.
        """
        if self.live_auto_execution:
            raise RuntimeError("CRITICAL: Exporter violated non-execution policy.")

        flattened_rows = []
        for report in reports:
            for trade in report.trades:
                duration_seconds = (trade.exit_time - trade.entry_time).total_seconds()
                row = {
                    "StrategyName": report.strategy_name,
                    "Symbol": trade.symbol,
                    "Direction": trade.direction,
                    "EntryTime": trade.entry_time.isoformat(),
                    "ExitTime": trade.exit_time.isoformat(),
                    "LifecycleDurationSeconds": duration_seconds,
                    "LifecycleDurationMinutes": round(duration_seconds / 60.0, 2),
                    "EntryPrice": trade.entry_price,
                    "ExitPrice": trade.exit_price,
                    "NetPnL": trade.pnl,
                    "PnLPercentage": trade.pnl_percentage,
                    "Outcome": trade.outcome,
                    "IsSuccessful": 1 if trade.outcome == "TARGET_HIT" else 0
                }
                flattened_rows.append(row)
                
        return flattened_rows

    def save_for_powerbi(self, reports: List[BacktestReport], filepath: str = "opportunity_lifecycle_powerbi.json"):
        """Exports flattened analytics payload to disk for Power BI consumption."""
        data = self.export_lifecycle_to_table(reports)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Exported {len(data)} opportunity lifecycle rows to {filepath} for Power BI.")
        return filepath
