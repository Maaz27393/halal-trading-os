---
id: SYS-ENTRY-RULES-001
type: system_rule
status: Active
version: 1.1
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed
---
## Related

Parent: [[Trading System]]

Strategy:
- [[EMA20-50 Pullback]]
- [[Breakout]]

SOP:
- [[Intraday SOP]]
-See [[Risk Management]]

---

# Entry Rules

## Live Execution Chain

1. Stock hits the Breakout Confirmation scanner → open chart.
2. Draw Anchored Volume Profile (AVP) for Intraday analysis.
3. Wait for pullback + bullish confirmation candle on the 15-minute chart.
4. Drop to the 5-minute chart → enter using the Long Position tool.
5. Set target using Pivot Points Standard → next resistance level.
6. Optional: check the 3-minute chart for candle-reversal confirmation.

## Style-Specific Entry Logic

### Intraday

- VWAP + EMA20 precision entries.
- Trading window: 9:15 AM–12:30 PM.

### Swing

- FRVP for structure.
- Patience-based setup.
- Target via Pivot Points Standard.

### BTST

- Day-high breakout + retest + volume/VWAP.
- Trading window: 3:10 PM–3:25 PM.

## Pre-Trade Requirements

- Uptrend confirmed.
- Entry at pullback.
- R:R ≥ 1:1.5.
- Position sizing ≤1% risk.
- Target defined.
- Stop-loss defined.
- 2–4 aligned confluence factors present.
- Market breadth checked.
- Correct time window for selected style.

## Rule Authority

This note contains approved entry rules migrated from the active Trading System.

Do not modify these rules based on individual trades or observations.

Any proposed change must follow:

Research → Evidence → Decision Log → Trading System update.