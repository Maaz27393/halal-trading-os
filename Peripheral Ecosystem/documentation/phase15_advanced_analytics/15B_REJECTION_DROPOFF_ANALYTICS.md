# 15B — Rejection / Drop-off Analytics Blueprint

## Overview
Rejection / Drop-off Analytics monitors and categorizes every trading opportunity that is filtered out, rejected, or abandoned before reaching final backtest simulation or live paper tracking. This identifies system bottlenecks, overly restrictive filter rules, and scanner noise.

## Rejection Taxonomy (Drop-off Stages)
1. **Shariah Compliance Filter:** Stocks failing Islamic financial screening criteria (debt-to-assets ratio, impermissible revenue, interest income threshold).
2. **Liquidity / Volume Filter:** Insufficient daily traded volume or average traded value (ADV).
3. **Technical Setup Filter:** Failure to meet core pattern criteria (e.g., failed moving average alignment, insufficient R:R ratio).
4. **Risk Management / Volatility Filter:** Excessive intraday volatility, wide spreads, or gapping risk.

## Power BI Data Schema Requirements
To analyze drop-offs in Power BI, scanner event logs must capture:
- `timestamp`: Exact time of evaluation
- `symbol`: Target ticker symbol
- `stage_dropped`: Phase where the opportunity was dropped (`SHARIAH_SCREEN`, `LIQUIDITY_CHECK`, `TECHNICAL_FILTER`, `RISK_CHECK`)
- `rejection_reason`: Specific narrative or error code explaining the drop-off
- `sector`: Industry sector (e.g., IT, Banking, Pharma)

## Key Power BI Measures
1. **Drop-off Rate by Stage (%):** `DIVIDE(CALCULATE(COUNTROWS(Rejections), Rejections[stage_dropped] = "SHARIAH_SCREEN"), COUNTROWS(Evaluations), 0)`
2. **Sector Leakage Index:** Visualizing which market sectors experience the highest drop-offs due to leverage or debt ratios.
3. **Opportunity Funnel Conversion:** Funnel chart showing progression from Raw Universe $\rightarrow$ Shariah Filter $\rightarrow$ Technical Scanner $\rightarrow$ Final Backtest Candidate.

## Governance Boundary
- **Telemetry Only:** Rejection logs are strictly read-only audit trails.
- **Non-Intervention:** Automatically filters out non-compliant items without overriding human or algorithmic governance boundaries (`LIVE_AUTO_EXECUTION = FALSE`).
