---
id: STRAT-002
type: strategy
status: Active
version: 1.1
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed

style: Intraday
market: NSE
asset: Equity
halal: true

risk_per_trade: 1%
target: 1.5R
---
# Breakout

## Objective

Execute the approved Breakout strategy using the documented scanner, market-condition, confirmation, risk and execution framework.

## Setup

Primary workflow:

Institution Accumulation
→ 120-Day High
→ Volume Range Expansion
→ Breakout Confirmation
→ Pullback / Retest
→ Confirmation
→ Entry

## Market Conditions

Use the approved 4-signal Go / No-Go framework:

1. NSE Advance > Decline
2. India VIX < 20
3. Nifty 50 trend positive
4. Stock EMA20 > EMA50

Scoring:

- 4/4 = Strong Go
- 3/4 = Go if setup is strong
- 2/4 = Caution; exceptional setups only
- 0–1/4 = Avoid

## Entry Framework

Confirm:

- Stock is in the approved Halal universe.
- Breakout condition is present.
- Pullback / retest confirmation is present where required.
- Volume confirmation is present.
- Required price structure / EMA confirmation is present.
- R:R ≥ 1:1.5.
- Risk ≤ 1% of applicable capital.

## Intraday Execution

Primary execution window:

**9:15 AM – 12:30 PM**

Secondary execution window:

**1:30 PM – 3:00 PM**

No fresh intraday entry after 3:00 PM.

## Target

Use the approved target-setting method:

**Pivot Points Standard → next relevant resistance**

Minimum planned R:R:

**1:1.5**

## Stop-Loss

- Define SL before entry.
- Anchor SL to the actual fill price.
- Never anchor SL/TP to `close`.

## Position Sizing

- Maximum risk = 1% of applicable capital.
- Maximum 2 positions per day globally.
- Second trade uses remaining available capital.
- Cash-only.
- No leverage or margin.

## Halal

Only approved Halal stocks may be traded.

## Exit

Use the approved exit framework:

1. Stop-Loss
2. Target
3. Matrix Technique behavioral trigger

## SOP

- [[Daily Pre Market SOP]]
- [[Intraday SOP]]

## Related Rules

- [[Entry Rules]]
- [[Exit Rules]]
- [[Risk Management]]
- [[Position Sizing]]
- [[Market Filters]]
- [[Halal Rules]]

## Research Status

Any proposed modification to the Breakout strategy must pass through:

Research
→ Evidence
→ Decision Log
→ Explicit Approval
→ Strategy / Trading System Update

## Trade History

```dataview
TABLE Date, Result, R
FROM "Trade Journal"
WHERE contains(Strategy, this.file.name)
SORT Date DESC

Decision History
TABLE Date, Decision
FROM "Decision Log"
WHERE contains(Strategy, this.file.name)
SORT Date DESC
