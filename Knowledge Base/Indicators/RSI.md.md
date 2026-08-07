# Relative Strength Index

## 1. What It Is

The **Relative Strength Index (RSI)** is a momentum oscillator developed by J. Welles Wilder Jr. that measures the velocity and magnitude of recent price movements on a bounded scale from 0 to 100.

## 2. How It Works

RSI measures the ratio of recent upward price changes to recent downward price changes over a specific lookback window (default: 14 periods). It evaluates whether an asset is overextended in speed, giving insights into overbought (>70), oversold (<30), and underlying structural divergence.

## 3. Formulas

1. **Calculate Initial Average Gain and Loss (N = 14):** $$Average\ Gain_1 = \frac{\sum Gains\ over\ last\ N\ periods}{N}$$ $$Average\ Loss_1 = \frac{\sum Losses\ over\ last\ N\ periods}{N}$$
    
2. **Wilder's Smoothing Method for Subsequent Periods:** $$Average\ Gain_t = \frac{(Average\ Gain_{t-1} \times (N-1)) + Current\ Gain}{N}$$ $$Average\ Loss_t = \frac{(Average\ Loss_{t-1} \times (N-1)) + Current\ Loss}{N}$$
    
3. **Calculate Relative Strength (RS) and RSI:** $$RS = \frac{Average\ Gain_t}{Average\ Loss_t}$$ $$RSI = 100 - \left(\frac{100}{1+RS}\right)$$
    

## 4. Key Signal Types

**Bullish Divergence:** Price prints a Lower Low (LL) while RSI prints a Higher Low (HL) → Signal: Potential Bullish Reversal

**Bearish Divergence:** Price prints a Higher High (HH) while RSI prints a Lower High (LH) → Signal: Potential Bearish Reversal

## 5. Strengths

- **Divergence Detection:** Bullish and bearish divergences between price and RSI are among the most reliable early-warning signals for momentum exhaustion.
- **Multi-Market Applicability:** Works consistently across stocks, forex, crypto, and commodities on any timeframe.
- **Regime Centerline Analysis:** The 50 level acts as a reliable filter — RSI > 50 indicates bullish regime control, while RSI < 50 indicates bearish regime control.

## 6. Weaknesses

- **Strong Trend Oversold/Overbought Traps:** In powerful bull runs, RSI can remain locked above 70 for extended periods while price continues soaring (and vice versa in bear runs).
- **Choppy Market Whipsaws:** Oscillates rapidly around the 50 mark during consolidation, leading to false signals.
- **Lagging Reversal Confirmation:** Divergence can persist across multiple higher highs before price finally turns.

## 7. Best Practices

- **Adjust Thresholds by Regime:**
    - _Bull Market Range:_ RSI fluctuates between 40 (support/oversold) and 80 (overbought).
    - _Bear Market Range:_ RSI fluctuates between 20 (oversold) and 60 (resistance/overbought).
- **Trade Divergence with Breakouts:** Never short on bearish divergence alone; wait for price to break key support or a trendline to confirm momentum loss.
- **Look for RSI Failure Swings:** A top failure swing occurs when RSI rises above 70, pulls back, fails to exceed 70 on the next push, and breaks its previous swing low.

## 8. Common Mistakes

- **Immediate Reversion Trading:** Blindly shorting every time RSI touches 70 or buying when RSI touches 30.
- **Ignoring Context:** Treating an RSI reading of 30 in a macro downtrend as a strong buy signal rather than a continuation setup.
- **Changing Default Parameters Unnecessarily:** Altering the 14-period setting without backtesting the effect on system signal-to-noise ratio.

## 9. Related Strategies

- RSI Divergence Reversal Strategy
- RSI Failure Swing Setup
- RSI-50 Centerline Regime Filter (using the midline alone as a trend-bias gate for entries)

## 10. Related Concepts

- [[MACD.md]]
- [[TrendAnalysis.md]]
- [[Patterns.md]]