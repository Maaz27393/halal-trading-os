# 15C — Scanner Performance Analytics Blueprint

## Overview
Scanner Performance Analytics measures the historical accuracy, yield, and signal-to-noise ratio of screening engines that populate your trading watchlist. It tracks whether scanner alerts convert into successful backtest targets or fail shortly after identification.

## Key Performance Indicators (KPIs)
1. **Scanner Hit Rate (%):** Percentage of flagged symbols that achieve a favorable price movement within a defined holding window (e.g., +2% within 3 hours).
2. **False Positive Ratio:** Percentage of scanner pings that immediately trigger a stop-loss or fail to break out past slippage buffers.
3. **Latency Impact:** Time elapsed between market breakout condition met and scanner notification/ingestion.
4. **Strategy Yield by Screener:** Correlating specific scanner rules (e.g., volume surge vs. opening range breakout) with net backtest PnL.

## Power BI Data Schema Requirements
To build the Scanner Performance dashboard in Power BI, log tables must include:
- `scanner_id`: Unique identifier for the screening rule (e.g., `MOMENTUM_BREAKOUT_V1`, `VOLUME_SURGE_HALAL`)
- `scan_timestamp`: Exact timestamp when the symbol matched scanner conditions
- `symbol`: Target asset ticker
- `matched_indicators`: JSON payload of values that triggered the alert (e.g., volume ratio, RSI, moving average alignment)
- `resulting_outcome`: Link to the backtest or lifecycle outcome (`TARGET_HIT`, `STOP_LOSS_HIT`, `EXPIRED`)

## Key Power BI Measures
1. **Screener Conversion Efficiency:** `DIVIDE(CALCULATE(COUNTROWS(Scans), Scans[resulting_outcome] = "TARGET_HIT"), COUNTROWS(Scans), 0)`
2. **Average Return per Scanner Signal:** `AVERAGE(Scans[pnl_percentage])`
3. **Scanner Ranking Matrix:** Comparative bar chart ranking screeners by net profitability and win rate.

## Governance Boundary
- **Observational Evaluation:** Scanners are evaluated purely on historical telemetry and simulated outcomes.
- **Non-Execution:** No automated trade triggers are sent directly from scanner output (`LIVE_AUTO_EXECUTION = FALSE`).
