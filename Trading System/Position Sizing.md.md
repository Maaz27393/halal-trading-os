---
id: SYS-POSITION-SIZING-001
type: system_rule
status: Active
version: 1.1
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed
---

# Position Sizing

## Risk Per Trade

- Maximum risk = **1% of total capital per stock**.
- Minimum R:R = **1:1.5** across Intraday, BTST and Swing.
- Maximum = **2 positions per day**, globally across all styles.

## Position-Sizing Formula

```text
qty = math.max(1, math.floor(riskAmount / riskPerShare))

Where:

- `riskAmount` = permitted monetary risk for the trade.
- `riskPerShare` = entry price − stop-loss price for a long position.
  
## Capital Sequencing

### Trade 1

Size against the full available capital using the 1% risk formula.

### Trade 2

If a second trade is taken:

- Use only the capital remaining after Trade 1.
- Apply the same 1% risk-sizing formula.
- Do not treat Trade 2 as if the full original capital were still available.

## Capital Restrictions

- Cash-only.
- No leverage.
- No margin.
- No F&O.
- No short selling.

## Position Limits

- Maximum 2 positions/day.
- The limit applies globally across Intraday, BTST and Swing.
- It is not 2 positions per style.

## Pre-Trade Checks

Before execution confirm:

- Risk ≤ 1% of applicable capital.
- R:R ≥ 1:1.5.
- Stop-loss defined.
- Target defined.
- Available cash confirmed.
- Position quantity calculated correctly.

## Authority

This note contains the approved position-sizing rules.

Any proposed change must follow:

Research → Evidence → Decision Log → Trading System update.

