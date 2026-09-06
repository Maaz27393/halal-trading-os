---
id: SYS-MARKET-FILTERS-001
type: system_rule
status: Active
version: 1.1
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed
---
# Market Filters

## Market Selection

### Market Breadth — Go / No-Go Framework

The following four signals form the market-breadth framework:

1. NSE Advance > Decline
2. India VIX below 20
3. Nifty 50 trend positive
4. Stock EMA20 above EMA50

All four signals do not have to pass for a trade to be considered.

Chartink/TradingView scanners may still identify strong individual stocks when the broader market is neutral.

## Execution Filters

The current documented execution filters are:

- Price > ₹500
- Market Cap > ₹2,000 Cr
- ROE > 11%
- Quick Ratio > 1
- Debt/Equity < 0.5
- India VIX preferred range: 15–18
- Avoid banking/finance stocks

## Trading Universe

- NSE equities
- Long-only
- Cash-only
- No leverage
- No short selling
- No derivatives

## Authority

This note contains market-selection/filter rules migrated from the active Trading System.

Do not change these rules based on individual trade observations.

Any proposed change must go through:

Research → Evidence → Decision Log → Trading System update.