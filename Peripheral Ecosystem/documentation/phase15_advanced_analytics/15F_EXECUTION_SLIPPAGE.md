# 15F — Execution & Slippage Analytics Blueprint

## Overview
Execution & Slippage Analytics evaluates the cost of market friction by measuring the variance between theoretical signal trigger prices and simulated execution prices. It quantifies the impact of slippage, brokerage fees, and bid-ask spreads on strategy profitability.

## Key Performance Indicators (KPIs)
1. **Average Slippage Cost (%):** Mean percentage difference between expected entry/exit prices and simulated filled prices.
2. **Friction Drag on Net PnL:** Cumulative reduction in portfolio return caused by brokerage commissions and slippage combined.
3. **Volatility-Slippage Correlation:** Analyzing how high intraday volatility spikes increase slippage variance across different asset classes.

## Power BI Data Schema Requirements
To build the Execution & Slippage dashboard in Power BI, trade logs must record:
- `symbol`: Ticker symbol
- `theoretical_price`: Price when signal was generated
- `executed_price`: Simulated entry or exit price after slippage adjustments
- `slippage_amount`: Absolute price variance (`abs(executed_price - theoretical_price)`)
- `slippage_percentage`: Percentage slippage relative to theoretical price
- `brokerage_fee`: Cost incurred per transaction

## Key Power BI Measures
1. **Total Friction Cost:** `SUM(Trades[slippage_amount]) + SUM(Trades[brokerage_fee])`
2. **Slippage Impact Ratio:** `DIVIDE(SUM(Trades[slippage_amount]), SUM(Trades[net_pnl]), 0)`
3. **Average Slippage by Volume Tier:** Grouping slippage by average traded volume to identify liquidity degradation limits.

## Governance Boundary
- **Simulation Analytics Only:** Evaluates friction models on historical or paper simulation data.
- **Non-Execution:** No live order routing or automated execution control hooks (`LIVE_AUTO_EXECUTION = FALSE`).
