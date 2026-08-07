#   Risk & Money Management

## 1. What It Is

**Risk Management** is the set of rules, mathematical calculations, and capital allocation strategies designed to protect trading capital from catastrophic loss and ensure long-term market survival.

## 2. How It Works

Trading is an exercise in managing probabilities; even high-win-rate strategies experience consecutive losses. Risk management restricts total capital risk per trade (typically the **1% Rule**) and uses precise position sizing to ensure no single loss threatens account solvency.

## 3. Formulas

1. **The 1% Capital Risk Rule:** $$Max\ Risk\ Amount\ ($) = Total\ Portfolio\ Capital \times 0.01$$
    
2. **Position Sizing Equation:** $$Position\ Size\ (Shares) = \frac{Max\ Risk\ Amount\ ($)}{|Entry\ Price - Stop\ Loss\ Price|}$$
    
3. **Required Return to Recoup Drawdown:** $$Recoup\ Return\ (%) = \left(\frac{1}{1-L} - 1\right) \times 100 \quad (L = Loss\ fraction)$$
    

## 4. The Recoup Table & Stop Loss Types

|Capital Lost (%)|Return Required to Recoup Capital (%)|Mathematical Reality / Consequence|
|---|---|---|
|−10%|+11.1%|Easily manageable recovery.|
|−20%|+25.0%|Requires solid performance streak.|
|−30%|+42.8%|Moderate recovery burden.|
|−50%|+100.0%|Must double remaining capital just to break even.|
|−60%|+150.0%|Exponential difficulty; extremely hard to recover.|

**Stop Loss Categories:**

1. **Physical Stop Loss** — Pre-set broker order on chart; execution is automatic. _(Recommended)_
2. **Trailing Stop Loss** — Automatically locks in profit as trade moves favorably.
3. **Time-Based Stop Loss** — Exits position if trade goes nowhere after X hours/days.
4. **Mental Stop Loss** — Unentered exit target; extremely vulnerable to emotional override. _(Avoid)_

## 5. Strengths

- **Guarantees Longevity:** Prevents a streak of bad trades from wiping out an account.
- **Removes Emotion:** Pre-calculated risk parameters eliminate panic and guesswork during live execution.
- **Asymmetric Compounding:** Keeping losses small enables massive long-term account growth through compound returns.

## 6. Weaknesses

- **Limits Short-Term Gains:** Capping position sizes prevents windfall profits on single winning trades.
- **Slippage Risk:** Market gaps during catastrophic black swan events can skip physical stop-loss levels.
- **Requires Disciplined Calculation:** Demands active mathematical calculation on every single order entry.

## 7. Best Practices

- **Enforce the 1% Rule:** Never risk more than 1% of total portfolio capital on any individual trade.
- **Decide Exit Before Entry:** Fix the physical stop-loss level _before_ determining position size or clicking buy.
- **Use Physical Stops Only:** Always enter hard stop orders into the broker platform rather than using mental stops.

## 8. Common Mistakes

- **Ignoring Asymmetric Drawdown Math:** Failing to realize that losing 50% of an account requires a 100% gain just to break even.
- **Averaging Down Losing Trades:** Adding more capital to a losing position ("martingaling") instead of taking the stop loss.
- **Risking Fixed Lot Sizes:** Trading the exact same number of shares/contracts regardless of stop loss distance.

## 9. Related Strategies

- Fixed 1% Capital Risk Sizing System
- ATR Dynamic Volatility Stop Loss Positioning
- Trailing Stop Profit Locking Strategy

## 10. Related Concepts

- [[../Performance Metrics/PerformanceMetrics.md|PerformanceMetrics.md]]
- [[../Statistics/Statistics.md|Statistics.md]]
- [[../Indicators/ATR.md|ATR.md]]