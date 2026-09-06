---
id: SOP-BACKTESTING-001
type: sop
status: Active
version: 1.1
created: 2026-08-08
updated: 2026-08-08
owner: Mohammed
---
# Backtesting SOP

## Purpose

Backtesting is used to evaluate a defined strategy or hypothesis using historical market data.

Backtest results are evidence for research and validation. They do not automatically become live Trading OS rules.

## 1. Strategy Definition

Before starting a backtest, document:

- Strategy name
- Exact entry conditions
- Exact exit conditions
- Stop-loss
- Target
- Position-sizing method
- Risk per trade
- Trading timeframe
- Trading style
- Stock universe
- Test period

The strategy must be defined before testing.

## 2. No Rule Changing During a Test

Do not modify entry, exit, risk or filter conditions during an active test because of observed results.

If a rule is changed:

- Record the change.
- Treat the modified version as a separate test.
- Do not combine results from different versions.

## 3. Data Requirements

Record:

- Data source
- Timeframe
- Historical period
- Stock universe
- Number of stocks tested
- Number of trades
- Any known data limitations

Do not present incomplete or unreliable data as validated evidence.

## 4. Test Integrity

Avoid:

- Look-ahead bias
- Future information leakage
- Repainting indicators
- Survivorship bias where relevant
- Changing rules after seeing results
- Selectively removing losing trades
- Cherry-picking stocks or periods

## 5. Performance Metrics

Where available, record:

- Total trades
- Winning trades
- Losing trades
- Win rate
- Profit Factor
- Net return
- Maximum drawdown
- Average R
- Expectancy
- Largest win
- Largest loss

Use the same methodology when comparing strategy variants.

## 6. Strategy Comparison

When comparing two versions:

- Keep the test period consistent.
- Keep the stock universe consistent where possible.
- Keep the risk methodology consistent.
- Change only the variable being tested.

Document exactly what changed between versions.

## 7. Validation

A backtest is not automatically validation.

Classify results as:

- Historical reference
- Research evidence
- Experimental evidence
- Validation evidence
- Accepted

The classification must reflect the actual evidence available.

## 8. Current Historical Backtest Status

The previous 153-stock 3-year/5-year EMA20/50 RSI Pullback backtests are **historical reference only**.

They evaluated the older strategy and do not validate the current multi-tool Trading OS.

The current system has evolved to include:

- FRVP
- AVP
- Volume analysis
- Pivot Points Standard
- Additional confluence rules

Therefore, the historical 153-stock results must not be presented as validation of the current system.

## 9. Current Data Status

There is currently no historical trade dataset requiring modification or migration.

Do not create synthetic historical trade results and present them as actual performance.

## 10. Research Integration

Backtest findings should be recorded in the Research system.

Workflow:

Hypothesis
→ Experimental Design
→ Backtest
→ Results
→ Interpretation
→ Decision

A positive backtest does not automatically change the Trading System.

## 11. Decision Gate

A strategy can move toward adoption only after sufficient evidence and the appropriate approval process.

Any change to an active Trading OS rule requires:
Research
→ Evidence
→ Decision Log
→ Explicit Approval
→ Trading System Update
→ Version Control
## Authority

This SOP governs the backtesting process.

It must not create new trading rules or convert historical results into live rules without formal approval.