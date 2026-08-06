## Volume Weighted Average Price

### 1. What It Is

The **Volume Weighted Average Price (VWAP)** is an intraday benchmark indicator that calculates the true average price an asset has traded at throughout a given session, weighted by both volume and price.

### 2. How It Works

VWAP aggregates every transaction within a trading session, multiplying the price by the volume traded at that price, and dividing by total cumulative volume. It resets to zero at the market open of every session. Because institutional orders (algorithms, hedge funds, market makers) are evaluated against VWAP performance, it serves as the ultimate benchmark for market value and fair liquidity.

### 3. Formulas

1. **Calculate Typical Price ($\text{TP}$):**
    
    $$\text{TP}_t = \frac{\text{High}_t + \text{Low}_t + \text{Close}_t}{3}$$
    
2. **Calculate Volume-Weighted Cumulative Sums:**
    
    $$\text{VWAP}_t = \frac{\sum_{i=1}^{t} (\text{TP}_i \times \text{Volume}_i)}{\sum_{i=1}^{t} \text{Volume}_i}$$
    
3. **Calculate Standard Deviation Bands (Optional):**
    
    $$\sigma_t = \sqrt{\frac{\sum (\text{TP}_i - \text{VWAP}_t)^2 \times \text{Volume}_i}{\sum \text{Volume}_i}}$$
    
    $$\text{Upper Band} = \text{VWAP}_t + (k \times \sigma_t)$$
    
    $$\text{Lower Band} = \text{VWAP}_t - (k \times \sigma_t)$$
    

### 4. Key Attributes & Mechanics

|**Attribute**|**Detail**|
|---|---|
|**Indicator Type**|Intraday Overlay (Benchmark / Value Tool)|
|**Primary Timeframes**|1-min, 5-min, 15-min intraday charts (or Anchored VWAP for multi-day)|
|**Key Levels**|VWAP Baseline (Fair Value), $+1\sigma / +2\sigma$ (Overbought), $-1\sigma / -2\sigma$ (Oversold)|

### 5. Strengths

- **Institutional Context:** Reflects real execution liquidity, making it far more reliable than pure price moving averages.
    
- **Intraday Bias Identification:** Prices consistently above VWAP signify strong buyer dominance; prices below indicate institutional distribution/selling.
    
- **Mean Reversion Utility:** Standard deviation bands around VWAP provide precise targets for mean-reversion counter-trend trades.
    

### 6. Weaknesses

- **Late-Session Inertia:** As total session volume accumulates throughout the day, late-day price moves require massive volume to shift the VWAP line, causing lag late in the session.
    
- **Intraday Reset Constraint:** Standard VWAP resets daily, making unanchored VWAP useless for multi-day swing trading analysis.
    
- **Not a Stationary Line:** During aggressive trend days, price can trend far away from VWAP without reverting to it until the session ends.
    

### 7. Best Practices

- **Institutional Execution Rule:** Look to enter long positions on pullbacks _near or at_ VWAP during an uptrend rather than chasing prices extended above VWAP.
    
- **Utilize Anchored VWAP (AVWAP):** Anchor VWAP manually to high-impact anchor points (e.g., earnings announcements, FOMC releases, swing highs/lows) to track structural value across days or weeks.
    
- **Trade Band Reversals in Ranges:** During flat market opens, treat $+2\sigma$ as resistance and $-2\sigma$ as support.
    

### 8. Common Mistakes

- **Using Standard VWAP on Daily Charts:** Expecting intraday VWAP code to work on daily/weekly candlestick charts without an anchor event.
    
- **Expecting Instant Bounces:** Treating VWAP as a razor-thin line of support rather than a flexible zone of fair value.
    
- **Ignoring Session Timing:** Blindly trusting VWAP signals during the first 15 minutes of market open when volume metrics are hyper-volatile and settling.