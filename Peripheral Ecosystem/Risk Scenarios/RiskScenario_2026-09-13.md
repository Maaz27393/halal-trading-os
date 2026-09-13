---
date: 2026-09-13
type: probabilistic-risk-scenario
scenarios_modeled: 2
guardrail: LIVE_AUTO_EXECUTION=FALSE
---

# Probabilistic Risk-Reward Scenario Model - 2026-09-13

## Overview
- **Scenarios Modeled**: 2
- **Methodology**: Mathematical expectation modeling using historical shadow attribution win rates and R:R ratios.

## Strategy Distribution Scenarios
### EMA Momentum Pullback (P4 Strategy)
- **Expected Win Rate**: `62.5%`
- **Average Reward-to-Risk**: `1.85`
- **Modeled Expected Value (EV)**: `0.38`
- **Distribution Bias**: `Right-Skewed (Favorable)`
### Volume Breakout Continuation
- **Expected Win Rate**: `51.0%`
- **Average Reward-to-Risk**: `2.4`
- **Modeled Expected Value (EV)**: `0.22`
- **Distribution Bias**: `Symmetric / High Volatility`

## Provenance & Analytical Caveats
- P6.2 Probabilistic Risk-Reward Scenario Modeler Active
- Analytical Note: Expected values derived from historical shadow distribution assumptions.
- Immutable Guardrail: LIVE_AUTO_EXECUTION = False
