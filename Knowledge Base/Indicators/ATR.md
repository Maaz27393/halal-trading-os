#  Average True Range

## 1. What It Is

The **Average True Range (ATR)** is a non-directional volatility indicator developed by J. Welles Wilder Jr. that measures market volatility by calculating the full range of asset price movement over a given period.

## 2. How It Works

Traditional range calculations (High − Low) fail to account for market gaps between trading sessions. ATR solves this by calculating the **True Range (TR)**, taking the maximum value among the current High/Low range and the distance from the prior candle's Close. It then applies a smoothed moving average to quantify overall volatility in absolute dollar/point terms.

## 3. Formulas

1. **Calculate True Range (TR):** $$TR_t = \max\big((High_t - Low_t),\ |High_t - Close_{t-1}|,\ |Low_t - Close_{t-1}|\big)$$
    
2. **Calculate Smoothed Average True Range (ATR over N = 14 periods):** $$ATR_t = \frac{(ATR_{t-1} \times (N-1)) + TR_t}{N}$$
    

## 4. Key Uses in Trading Systems

1. **Volatility-Based Stop Loss:** `Stop Distance = Entry Price − (Multiplier × ATR)` _Example: Entry $100, ATR = $2.00, Multiplier = 2× → Stop Loss = $100 − (2 × $2.00) = $96.00_
    
2. **Position Sizing:** `Position Size = Account Risk ($) / (Multiplier × ATR)`
    

## 5. Strengths

- **Objective Volatility Benchmark:** Provides an exact numerical figure showing how much an asset typically moves per candle.
- **Dynamic Stop Losses:** Prevents traders from getting prematurely stopped out by normal market noise in high-volatility environments.
- **Equalizes Portfolio Risk:** Allows traders to normalize position sizes across assets with drastically different volatility profiles (e.g., matching risk on a low-ATR utility stock vs. a high-ATR tech stock).
- **Breakout Precursor (Volatility Squeezes):** Multi-period contractions in ATR often precede violent trend expansion moves.

## 6. Weaknesses

- **Non-Directional:** ATR measures magnitude, not direction; an exploding ATR line simply means volatility is expanding — whether price is crashing or skyrocketing.
- **Absolute Value Bias:** ATR is expressed in raw currency/points (e.g., $4.50), making it impossible to directly compare the ATR of a $20 stock with a $500 stock without normalizing to a percentage (ATR / Price × 100%).
- **Lags Sudden Volatility Shocks:** Because ATR is a smoothed average over 14 periods, a single massive candle takes time to fully shift the indicator level.

## 7. Best Practices

- **Chandelier Exit Implementation:** Trail stops using 2.5 × ATR or 3 × ATR below the highest high of the trend to capture full swing moves.
- **Combine with Directional Tools:** Use ATR for trade management (stop placement and target calculation) while using price action or moving averages for directional bias.
- **Watch for ATR Contraction:** Look for assets where ATR drops to multi-month lows to position for upcoming breakout trades.

## 8. Common Mistakes

- **Using ATR as a Directional Trigger:** Buying an asset simply because the ATR line is rising.
- **Fixed-Point Stops across Different ATR Environments:** Using a fixed 20-pip or $1.00 stop loss regardless of whether market volatility is low or high.
- **Ignoring Timeframe Impact:** Expecting a 5-minute ATR value to provide valid risk parameters for daily swing trade setups.

## 9. Related Strategies

- ATR Chandelier Exit Trailing Stop System
- ATR Volatility Contraction Breakout System
- ATR-Normalized Position Sizing Across Assets

## 10. Related Concepts

- [[Risk.md]]
- [[TrendAnalysis.md]]
- [[BollingerBands.md]]