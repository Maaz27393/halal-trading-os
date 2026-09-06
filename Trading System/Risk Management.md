---
id: SYS-RISK-MANAGEMENT-001
type: system_rule
status: Active
version: 1.1
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed
---
# Risk Management

## Core Risk Rules

- Maximum risk per stock = **1% of applicable capital**.
- Minimum R:R = **1:1.5** across all trading styles.
- Maximum = **2 positions per day**, globally across Intraday, BTST and Swing.

## Capital

- Cash-only trading.
- No leverage.
- No margin.
- No F&O.
- No short selling.

## Stop-Loss and Target

- Stop-loss must be defined before execution.
- Target must be defined before execution.
- SL/TP are anchored to the **actual fill price**.
- Never anchor SL/TP to `close`.

## Capital Sequencing

### Trade 1

Use the full available capital as the basis for the 1% risk calculation.

### Trade 2

If taken:

- Use only capital remaining after Trade 1.
- Apply the same 1% risk calculation.
- Do not recalculate as though the original full capital were still available.

## Risk Calculation


riskAmount = applicableCapital × 1%

riskPerShare = Entry Price − Stop-Loss Price

qty = math.max(1, math.floor(riskAmount / riskPerShare))

## Pre-Trade Risk Check

Before execution confirm:

- [ ]  Risk ≤ 1%
- [ ]  R:R ≥ 1:1.5
- [ ]  Stop-loss defined
- [ ]  Target defined
- [ ]  Cash available
- [ ]  Position quantity calculated
- [ ]  Daily position limit not exceeded

## Behavioral Risk Control

Use the Matrix Technique:

> "Am I following my plan?"

If the answer is **No**:

- Exit immediately.
- Stop trading for the day.

## Operational Safety

Kite Custom connector remains read-only by default.

No order placement, modification or cancellation without explicit in-chat instruction for that trading day.

## Authority

This note contains approved risk-management rules migrated from the Trading System and Decisions Log.

Any proposed change must follow:

Research → Evidence → Decision Log → Trading System update.