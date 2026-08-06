

---
---
---
id: STRAT-001
type: strategy
status: Active
version: 2.0
created: 2026-08-06
updated: 2026-08-06
owner: Mohammed

style: Intraday
timeframe: 5m
market: NSE
asset: Equity
halal: true

risk_per_trade: 1%
target: 1.5R
---
---
---

---
# EMA20-50 Pullback

## Objective

...

---

## Rules

![[Entry Rules]]

![[Exit Rules]]

![[Risk Management]]

![[Market Filters]]

---

## SOP

![[Intraday SOP]]

---

## Trade History

```dataview
TABLE Date, Result, R
FROM "Trade Journal"
WHERE contains(Strategy, this.file.name)
SORT Date DESC
---

# Decision History
TABLE Date, Decision
FROM "Decision Log"
WHERE contains(Strategy, this.file.name)
SORT Date DESC


---

# Trade Journals

Every trade using this strategy should link back here.

---

# Improvements

-## References

Rules:
- [[Entry Rules]]
- [[Exit Rules]]
- [[Risk Management]]

SOP:
- [[Intraday SOP]]

Journal:
- [[Trade Journal]]

Decisions:
- [[Decision Log]]