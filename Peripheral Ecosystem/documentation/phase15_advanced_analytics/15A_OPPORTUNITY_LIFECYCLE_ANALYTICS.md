# 15A — Opportunity Lifecycle Analytics Blueprint

## Overview
Opportunity Lifecycle Analytics tracks a trading setup from initial detection/scanner alert through validation, simulation, and final outcome. 

## Power BI Data Schema Requirements
To build the Opportunity Lifecycle dashboard in Power BI, the backtesting engine exports structured logs with the following core fields:
- `symbol`: Ticker symbol (e.g., RELIANCE, INFY)
- `direction`: Trade direction (`LONG` / `SHORT`)
- `discovery_timestamp`: Timestamp when the opportunity was first flagged
- `validation_timestamp`: Timestamp when filters/rules were verified
- `simulation_timestamp`: Timestamp when backtest execution occurred
- `exit_timestamp`: Timestamp when the trade concluded
- `lifecycle_duration_seconds`: Total elapsed time from discovery to completion
- `outcome`: Final state (`TARGET_HIT`, `STOP_LOSS_HIT`, `EXPIRED`)
- `net_pnl`: Net monetary profit or loss after slippage and brokerage
- `pnl_percentage`: Percentage return on capital

## Key Power BI Measures
1. **Conversion Success Rate (%):** `DIVIDE(COUNTROWS(FILTER(Trades, Trades[outcome] = "TARGET_HIT")), COUNTROWS(Trades), 0)`
2. **Average Lifecycle Duration (Hours):** `AVERAGE(Trades[lifecycle_duration_seconds]) / 3600`
3. **Lifecycle Efficiency Index:** Ratio of profitable trade duration versus adverse draw-down duration.

## Governance Boundary
- **Observational Only:** All data feeds into Power BI via batch exports or read-only JSON/CSV sinks.
- **Non-Execution:** No bi-directional write hooks to live brokerage accounts.
