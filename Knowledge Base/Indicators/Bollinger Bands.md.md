## Bollinger Bands

### 1. What It Is

**Bollinger Bands** are a multi-purpose technical analysis tool developed by John Bollinger in the early 1980s. They consist of a center moving average and two outer envelope bands whose distance is dynamically determined by the standard deviation of price changes.

### 2. How It Works

Bollinger Bands adjust automatically to expanding and contracting market volatility. The center line is typically a 20-period Simple Moving Average (SMA). The upper and lower bands are placed standard deviations (usually $2.0$) above and below this center line. Because standard deviation measures volatility, the bands widen during volatile periods and contract during quiet, low-volatility periods. Mathematically, approximately 95% of price action takes place within $\pm 2$ standard deviations of the mean under a normal distribution.

### 3. Formulas

Standard settings: $N = 20$ periods, $K = 2.0$ standard deviation multiplier.

1. **Middle Band ($\text{MB}$):**
    
    $$\text{MB}_t = \text{SMA}_N(\text{Close}_t) = \frac{\sum_{i=1}^{N} \text{Close}_i}{N}$$
    
2. **Standard Deviation ($\sigma$):**
    
    $$\sigma_t = \sqrt{\frac{\sum_{i=1}^{N} (\text{Close}_i - \text{MB}_t)^2}{N}}$$
    
3. **Upper Band ($\text{UB}$) & Lower Band ($\text{LB}$):**
    
    $$\text{UB}_t = \text{MB}_t + (K \times \sigma_t)$$
    
    $$\text{LB}_t = \text{MB}_t - (K \times \sigma_t)$$
    
4. **Derived Metrics:**
    
    $$\%B = \frac{\text{Close}_t - \text{LB}_t}{\text{UB}_t - \text{LB}_t}$$
    
    $$\text{Bandwidth} = \frac{\text{UB}_t - \text{LB}_t}{\text{MB}_t}$$
    

### 4. Key Setup Patterns & Mechanics

```
1. THE BOLLINGER SQUEEZE (Volatility Expansion Setup):
   Bandwidth reaches multi-period low → Extreme compression
   Action: Prepare for explosive breakout in direction of volume follow-through.

2. WALKING THE BANDS (Strong Trend Continuation):
   Price hugs or pushes along Upper Band (Uptrend) or Lower Band (Downtrend)
   Interpretation: High momentum, NOT an automatic sell signal.

3. DOUBLE BOTTOM / TOP REVERSAL (W-Bottom or M-Top):
   First low touches/pierces Lower Band → Rally to Middle Band → Second low stays ABOVE Lower Band
   Signal: High-probability bullish structural turnaround.
```

|**Metric**|**Calculation / Zone**|**Purpose / Trading Application**|
|---|---|---|
|**Middle Band**|20 SMA|Dynamic baseline support/resistance in healthy trends|
|**Upper Band**|$\text{SMA} + 2\sigma$|High-volatility boundary / overextended condition indicator|
|**Lower Band**|$\text{SMA} - 2\sigma$|Low-volatility boundary / discounted condition indicator|
|**Bandwidth**|$(\text{UB} - \text{LB}) / \text{MB}$|Identifies volatility squeezes and volatility tops|
|**%B Indicator**|$(\text{Close} - \text{LB}) / (\text{UB} - \text{LB})$|Measures exact relative location of price within the bands ($>1$ = above upper band, $<0$ = below lower band)|

### 5. Strengths

- **Dynamic Volatility Adaptation:** Unlike static envelope channels, bands automatically widen during high volatility and shrink during low volatility.
    
- **Clear Volatility Squeeze Detection:** Uniquely effective at pinpointing periods of extreme price compression that precede strong trend breakouts.
    
- **Versatile Across Regimes:** Functions effectively for both range-bound mean-reversion tactics and trend breakout systems.
    

### 6. Weaknesses

- **Band Tagging Misinterpretation:** Touching an outer band is not inherently a sell/buy signal; during strong trends, price can "walk the bands" for long periods.
    
- **Simple Moving Average Lag:** The 20 SMA middle band uses equal weighting, which can lag sudden price shifts compared to exponential measures.
    
- **False Breakout Risk from Squeezes:** A Bollinger Squeeze often produces a head-fake (fake breakout in one direction before the real explosive trend begins).
    

### 7. Best Practices

- **Combine with Volume for Squeeze Breakouts:** Require volume expansion on the day of a band breakout to confirm validity and avoid head-fakes.
    
- **Use %B for Quantifiable Divergences:** Identify bullish divergence when price makes a lower low but $\%B$ makes a higher low (staying inside the lower band).
    
- **Adapt Multipliers to Strategy:** Use $K = 2.0$ for standard 20 SMA, but consider $K = 1.9$ for shorter lookbacks (10-period) or $K = 2.1$ for longer lookbacks (50-period).
    

### 8. Common Mistakes

- **Blind Reversal Selling at Upper Band:** Shorting every upper band touch during a runaway bull market, getting crushed as price walks the upper band.
    
- **Ignoring Bandwidth Context:** Entering mean-reversion trades when Bandwidth is expanding rapidly (runaway trend mode).
    
- **Using Outer Bands as Absolute Hard Stops:** Placing tight stop-loss orders directly on the outer bands, which are prone to being swept by price wicks.