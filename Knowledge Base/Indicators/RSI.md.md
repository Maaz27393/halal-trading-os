## Relative Strength Index

### 1. What It Is

The **Relative Strength Index (RSI)** is a momentum oscillator developed by J. Welles Wilder Jr. that measures the velocity and magnitude of recent price movements on a bounded scale from 0 to 100.

### 2. How It Works

RSI measures the ratio of recent upward price changes to recent downward price changes over a specific lookback window (default: 14 periods). It evaluates whether an asset is overextended in speed, giving insights into overbought ($>70$), oversold ($<30$), and underlying structural divergence.

### 3. Formulas

1. **Calculate Initial Average Gain and Loss ($N = 14$):**
    
    $$\text{Average Gain}_1 = \frac{\sum \text{Gains over last } N \text{ periods}}{N}$$
    
    $$\text{Average Loss}_1 = \frac{\sum \text{Losses over last } N \text{ periods}}{N}$$
    
2. **Wilder's Smoothing Method for Subsequent Periods:**
    
    $$\text{Average Gain}_t = \frac{(\text{Average Gain}_{t-1} \times (N - 1)) + \text{Current Gain}}{N}$$
    
    $$\text{Average Loss}_t = \frac{(\text{Average Loss}_{t-1} \times (N - 1)) + \text{Current Loss}}{N}$$
    
3. **Calculate Relative Strength ($\text{RS}$) and $\text{RSI}$:**
    
    $$\text{RS} = \frac{\text{Average Gain}_t}{\text{Average Loss}_t}$$
    
    $$\text{RSI} = 100 - \left( \frac{100}{1 + \text{RS}} \right)$$
    

### 4. Key Signal Types

```
BULLISH DIVERGENCE:                           BEARISH DIVERGENCE:
Price:   Lower Low (LL)   ↘                   Price:   Higher High (HH)  ↗
RSI:     Higher Low (HL)  ↗                   RSI:     Lower High (LH)   ↘
Signal: Potential Bullish Reversal             Signal: Potential Bearish Reversal
```

### 5. Strengths

- **Divergence Detection:** Bullish and Bearish divergences between price and RSI are among the most reliable early-warning signals for momentum exhaustion.
    
- **Multi-Market Applicability:** Works consistently across stocks, forex, crypto, and commodities on any timeframe.
    
- **Regime Centerline Analysis:** The 50 level acts as a reliable filter: RSI $> 50$ indicates bullish regime control, while RSI $< 50$ indicates bearish regime control.
    

### 6. Weaknesses

- **Strong Trend Oversold/Overbought Traps:** In powerful bull runs, RSI can remain locked above 70 for extended periods while price continues soaring (and vice versa in bear runs).
    
- **Choppy Market Whipsaws:** Oscillates rapidly around the 50 mark during consolidation, leading to false signals.
    
- **Lagging Reversal Confirmation:** Divergence can persist across multiple higher highs before price finally turns.
    

### 7. Best Practices

- **Adjust Thresholds by Regime:**
    
    - **Bull Market Range:** RSI fluctuates between 40 (support/oversold) and 80 (overbought).
        
    - **Bear Market Range:** RSI fluctuates between 20 (oversold) and 60 (resistance/overbought).
        
- **Trade Divergence with Breakouts:** Never short on bearish divergence alone; wait for price to break key support or a trendline to confirm momentum loss.
    
- **Look for RSI Failure Swings:** A top failure swing occurs when RSI rises above 70, pulls back, fails to exceed 70 on the next push, and breaks its previous swing low.
    

### 8. Common Mistakes

- **Immediate Reversion Trading:** Blindly shorting every time RSI touches 70 or buying when RSI touches 30.
    
- **Ignoring Context:** Treating an RSI reading of 30 in a macro downtrend as a strong buy signal rather than a continuation setup.
    
- **Changing Default Parameters Unnecessarily:** Altering the 14-period setting without backtesting the effect on system signal-to-noise ratio.