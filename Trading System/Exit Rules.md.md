---
id: SYS-EXIT-RULES-001
type: system_rule
status: Active
version: 1.1
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed
---
# Exit Rules

## Universal Exit Rules

- Stop-loss and target are set at entry, before execution.
- SL/TP must be anchored to the actual fill price, never to `close`.
- Target is set using Pivot Points Standard → next resistance level.
- Exit when the predefined Stop-Loss, predefined Target, or approved behavioral exit trigger occurs first.

## Matrix Technique

Before taking any emotional action, ask:

> "Am I following my plan?"

If the answer is **No**:

- Exit immediately.
- Stop trading for the day.

## BTST Exit Rules

### Gap-Up Open

- Book partial profit quickly.
- Do not hold blindly.

### Flat / Weak Open

- Exit immediately.

## Intraday Exit Rules

Currently approved mechanisms:

1. Predefined Stop-Loss
2. Predefined Target
3. Matrix Technique behavioral trigger

### Not Currently Approved

- No intraday trailing-stop rule.
- No intraday partial-profit rule.

These remain future research items and must not be treated as active rules.

## Exit Discipline

Never:

- Move the stop-loss emotionally.
- Modify the target after entry without an approved system rule.
- Hold a position because of hope.
- Override the Matrix Technique.

## Authority

These are the currently approved Trading System exit rules.

Any proposed modification must follow:

Research → Evidence → Decision Log → Trading System update.