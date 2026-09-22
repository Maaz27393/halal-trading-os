# 15G — Trade Outcome Attribution Blueprint

## Overview
Trade Outcome Attribution deconstructs portfolio performance by isolating the underlying drivers of wins and losses. It attributes trade PnL across strategy types, market sectors, entry timeframes, and macroeconomic indicator states.

## Core Attribution Dimensions
1. **Strategy Attribution:** Which specific trading rules or breakout models generated the highest net PnL?
2. **Sector Attribution:** Which industry sectors (e.g., Information Technology, Pharmaceuticals, Banking) delivered optimal risk-adjusted returns under current Halal constraints?
3. **Time-of-Day Attribution:** Analyzing opening volatility vs. mid-day consolidation vs. closing momentum performance.
4. **Macro Correlation:** Linking trade success rates with macroeconomic indicators (e.g., high vs. low inflation or repo rate regimes).

## Power BI Data Schema Requirements
To build the Trade Outcome Attribution dashboard in Power BI, data models must join trade results with contextual metadata:
- `trade_id`: Unique trade identifier
- `strategy_name`: Strategy identifier (e.g., `BreakoutStrategy`, `MomentumV1`)
- `sector`: Industry classification
- `entry_hour`: Hour of day when trade was initiated
- `macro_regime`: Prevailing macroeconomic state snapshot
- `net_pnl`: Monetary profit or loss
- `outcome`: Final outcome (`TARGET_HIT`, `STOP_LOSS_HIT`, `EXPIRED`)

## Key Power BI Measures
1. **Net PnL Contribution by Sector:** `CALCULATE(SUM(Trades[net_pnl]), ALLEXCEPT(Trades, Trades[sector]))`
2. **Strategy Profit Factor:** `DIVIDE(CALCULATE(SUM(Trades[net_pnl]), Trades[net_pnl] > 0), ABS(CALCULATE(SUM(Trades[net_pnl]), Trades[net_pnl] < 0)), 0)`
3. **Optimal Trading Window Efficiency:** Average PnL grouped by 30-minute market intervals.

## Governance Boundary
- **Retrospective Analytics:** Evaluates historical and simulated trade outcomes.
- **Non-Execution:** No live trading feedback loops or autonomous strategy tuning (`LIVE_AUTO_EXECUTION = FALSE`).
