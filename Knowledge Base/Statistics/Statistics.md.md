#  Statistical Trading Analysis

## 1. What It Is

**Statistical Trading Analysis** is the quantitative evaluation of trading performance metrics over a large sample size of trades to verify a strategy's mathematical edge.

## 2. How It Works

Traders calculate historical win rates, loss rates, and average profit/loss sizes to establish **Strategy Expectancy**. A positive expectancy mathematically guarantees that, over a statistically significant sample size (Law of Large Numbers), the trading system will produce positive capital growth.

## 3. Formulas

1. **Mathematical Strategy Expectancy:** $$E = (Win\ Rate \times Average\ Win) - (Loss\ Rate \times Average\ Loss)$$
    
2. **Win Rate / Loss Rate Equation:** $$Win\ Rate\ (W) = \frac{Total\ Winning\ Trades}{Total\ Trades\ Executed}$$ $$Loss\ Rate\ (L) = 1 - W$$
    
3. **Profit Factor:** $$Profit\ Factor = \frac{Gross\ Profits\ ($)}{Gross\ Losses\ ($)}$$
    

## 4. Expectancy & Sample Size Analysis

**Expectancy Scenario Comparison:**

_System A (High Win Rate / Low R:R):_ Win Rate 70%, Avg Win $100, Avg Loss $200 Expectancy = (0.70 × 100) − (0.30 × 200) = $70 − $60 = **+$10 per trade**

_System B (Low Win Rate / High R:R):_ Win Rate 40%, Avg Win $300, Avg Loss $100 Expectancy = (0.40 × 300) − (0.60 × 100) = $120 − $60 = **+$60 per trade (superior edge)**

This illustrates why win rate alone is a misleading performance metric — System B wins less often but produces 6× the expectancy of System A due to its superior risk-to-reward structure.

|Metric|Minimum Viable Threshold|Target Benchmark|Meaning / Purpose|
|---|---|---|---|
|Expectancy (E)|> 0.00|> 0.5 × Average Loss|Net expected dollar profit per dollar risked over time.|
|Profit Factor|> 1.25|> 2.00|Ratio of total profits generated to total capital lost.|
|Sample Size (N)|> 30 trades|> 100 backtested trades|Minimum sample required to satisfy statistical significance.|

## 5. Strengths

- **Removes Subjectivity:** Replaces emotional hope with empirical mathematical data.
- **Validates Edge:** Confirms whether a trading setup actually works before committing real capital.
- **Instills Trade Confidence:** Knowing a strategy has positive expectancy helps traders handle inevitable losing streaks without abandon.

## 6. Weaknesses

- **Overfitting / Curve Fitting Risk:** Tweaking strategy rules excessively to fit historical data can lead to real-world forward failure.
- **Non-Stationary Markets:** Past market conditions used in backtests may shift due to changing macro regimes.
- **Requires Large Data Sets:** Demands logging dozens to hundreds of trades to attain statistical validity.

## 7. Best Practices

- **Evaluate Over Sample Sizes:** Judge strategy performance over blocks of 30 to 100 trades rather than outcome-by-outcome.
- **Focus on Expectancy Over Win Rate:** Prioritize higher Risk-to-Reward ratios over high win rates.
- **Forward-Test via Paper Trading:** Validate backtested statistical models in live, real-time market conditions before scaling capital.

## 8. Common Mistakes

- **Obsessing Over Win Rate:** Chasing a 90% win rate while taking massive unmanaged losses that destroy net expectancy.
- **Abandoning Systems Early:** Changing strategies after a 3-trade losing streak without reaching statistical sample size.
- **Ignoring Commission / Slippage Costs:** Failing to deduct broker commissions and execution slippage from expectancy equations.

## 9. Related Strategies

- Systematic Positive Expectancy Scalping
- Asymmetric Risk-Reward Trend System
- Quant Backtested Breakout Model

## 10. Related Concepts

- [[PerformanceMetrics.md]]
- [[Risk.md]]
- [[TradingPsychology.md]]