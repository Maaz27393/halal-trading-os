#  Bollinger Bands

## 1. What It Is

**Bollinger Bands** are a multi-purpose technical analysis tool developed by John Bollinger in the early 1980s. They consist of a center moving average and two outer envelope bands whose distance is dynamically determined by the standard deviation of price changes.

## 2. How It Works

Bollinger Bands adjust automatically to expanding and contracting market volatility. The center line is typically a 20-period Simple Moving Average (SMA). The upper and lower bands are placed standard deviations (usually 2.0) above and below this center line. Because standard deviation measures volatility, the bands widen during volatile periods and contract during quiet, low-volatility periods. Mathematically, approximately 95% of price action takes place within ±2 standard deviations of the mean under a normal distribution.

## 3. Formulas

Standard settings: N = 20 periods, K = 2.0 standard deviation multiplier.

1. **Middle Band (MB):** $$MB_t = SMA_N(Close_t) = \frac{\sum_{i=1}^{N} Close_i}{N}$$
    
2. **Standard Deviation (σ):** $$\sigma_t = \sqrt{\frac{\sum_{i=1}^{N} (Close_i - MB_t)^2}{N}}$$
    
3. **Upper Band (UB) & Lower Band (LB):** $$UB_t = MB_t + (K \times \sigma_t)$$ $$LB_t = MB_t - (K \times \sigma_t)$$
    
4. **Derived Metrics:** $$%B = \frac{Close_t - LB_t}{UB_t - LB_t}$$ $$Bandwidth = \frac{UB_t - LB_t}{MB_t}$$
    

## 4. Key Setup Patterns & Mechanics

1. **The Bollinger Squeeze (Volatility Expansion Setup):** Bandwidth reaches a multi-period low → extreme compression. _Action: prepare for an explosive breakout in the direction of volume follow-through._
2. **Walking the Bands (Strong Trend Continuation):** Price hugs or pushes along the Upper Band (uptrend) or Lower Band (downtrend). _Interpretation: high momentum, NOT an automatic sell signal._
3. **Double Bottom / Top Reversal (W-Bottom or M-Top):** First low touches/pierces the Lower Band → rally to the Middle Band → second low stays above the Lower Band. _Signal: high-probability bullish structural turnaround._

|Metric|Calculation / Zone|Purpose / Trading Application|
|---|---|---|
|Middle Band|20 SMA|Dynamic baseline support/resistance in healthy trends|
|Upper Band|SMA + 2σ|High-volatility boundary / overextended condition indicator|
|Lower Band|SMA − 2σ|Low-volatility boundary / discounted condition indicator|
|Bandwidth|(UB − LB) / MB|Identifies volatility squeezes and volatility tops|
|%B Indicator|(Close − LB) / (UB − LB)|Measures exact relative location of price within the bands (>1 = above upper band, <0 = below lower band)|

## 5. Strengths

- **Dynamic Volatility Adaptation:** Unlike static envelope channels, bands automatically widen during high volatility and shrink during low volatility.
- **Clear Volatility Squeeze Detection:** Uniquely effective at pinpointing periods of extreme price compression that precede strong trend breakouts.
- **Versatile Across Regimes:** Functions effectively for both range-bound mean-reversion tactics and trend breakout systems.

## 6. Weaknesses

- **Band Tagging Misinterpretation:** Touching an outer band is not inherently a sell/buy signal; during strong trends, price can "walk the bands" for long periods.
- **Simple Moving Average Lag:** The 20 SMA middle band uses equal weighting, which can lag sudden price shifts compared to exponential measures.
- **False Breakout Risk from Squeezes:** A Bollinger Squeeze often produces a head-fake (fake breakout in one direction before the real explosive trend begins).

## 7. Best Practices

- **Combine with Volume for Squeeze Breakouts:** Require volume expansion on the day of a band breakout to confirm validity and avoid head-fakes.
- **Use %B for Quantifiable Divergences:** Identify bullish divergence when price makes a lower low but %B makes a higher low (staying inside the lower band).
- **Adapt Multipliers to Strategy:** Use K = 2.0 for standard 20-period SMA, but consider K = 1.9 for shorter lookbacks (10-period) or K = 2.1 for longer lookbacks (50-period).

## 8. Common Mistakes

- **Blind Reversal Selling at Upper Band:** Shorting every upper band touch during a runaway bull market, getting crushed as price walks the upper band.
- **Ignoring Bandwidth Context:** Entering mean-reversion trades when Bandwidth is expanding rapidly (runaway trend mode).
- **Using Outer Bands as Absolute Hard Stops:** Placing tight stop-loss orders directly on the outer bands, which are prone to being swept by price wicks.

## 9. Related Strategies

- Bollinger Squeeze Breakout System
- %B Divergence Reversal Strategy
- Walking the Bands Trend Continuation

## 10. Related Concepts

 - [[ATR.md]]
- [[../Volume Analysis/VolumeAnalysis.md|VolumeAnalysis.md]]
 - [[../Candlesticks/Candlesticks.md|Candlesticks.md]]