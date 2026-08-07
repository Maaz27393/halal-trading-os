# Moving Average Convergence Divergence

## 1. What It Is

The **Moving Average Convergence Divergence (MACD)** is a versatile trend-following momentum indicator created by Gerald Appel in the late 1970s. It shows the relationship between two exponential moving averages (EMAs) of an asset's price to gauge trend direction, momentum strength, and potential reversal points.

## 2. How It Works

The MACD converts two trend-following moving averages into a momentum oscillator by subtracting the longer-term EMA from the shorter-term EMA. The result oscillates above and below a central **Zero Line**. A third line, known as the **Signal Line** (an EMA of the MACD line itself), is plotted on top to act as a trigger for buy and sell decisions. Additionally, a **MACD Histogram** visually represents the distance between the MACD line and the Signal Line, offering early visual warnings of momentum expansion or deceleration.

## 3. Formulas

The standard parameters for MACD are (12, 26, 9), representing the fast period, slow period, and signal period respectively.

1. **Calculate the MACD Line:** $$MACD\ Line_t = EMA_{12}(Close_t) - EMA_{26}(Close_t)$$
    
2. **Calculate the Signal Line:** $$Signal\ Line_t = EMA_9(MACD\ Line_t)$$
    
3. **Calculate the MACD Histogram:** $$Histogram_t = MACD\ Line_t - Signal\ Line_t$$
    

## 4. Key Signal Types & Mechanics

**Bullish Signal Line Crossover:** MACD Line crosses above Signal Line; Histogram turns positive (bars above 0) → Signal: Bullish Momentum Acceleration

**Bearish Signal Line Crossover:** MACD Line crosses below Signal Line; Histogram turns negative (bars below 0) → Signal: Bearish Momentum Acceleration

**Zero-Line Crossover:** MACD Line crosses above 0 (short-term EMA-12 > long-term EMA-26) → Bullish Trend Regime. MACD Line crosses below 0 (EMA-12 < EMA-26) → Bearish Trend Regime.

|Component|Description|Interpretation|
|---|---|---|
|**MACD Line**|12 EMA − 26 EMA|Velocity of price move; distance from zero shows distance between EMAs|
|**Signal Line**|9 EMA of MACD|Smoothed trigger line for entry and exit timing|
|**Histogram**|MACD − Signal|Bar height indicates momentum speed; shrinking bars show momentum decay|

## 5. Strengths

- **Dual Functionality:** Combines trend-following characteristics (via EMAs) with momentum measuring (via oscillator structure) in a single tool.
- **Early Reversal Detection:** The MACD Histogram often turns over before price actually reverses, providing advance warning of trend deceleration.
- **Objective Crossovers:** Provides clear, quantifiable rules for signal crossovers, making it ideal for algorithmic and systematic strategies.
- **Effective Divergence Signals:** Regular and hidden divergences between MACD and price provide powerful market turnaround clues.

## 6. Weaknesses

- **Lagging Indicator:** Because MACD is based on moving averages, signals lag price turns; by the time a crossover occurs, a large portion of the move may already be over.
- **False Signals in Ranging Markets:** Frequently whipsaws back and forth around the zero line during tight consolidation phases, producing low-probability signals.
- **Unbounded Scale:** MACD values are not bounded (unlike RSI which is 0–100), making it difficult to define fixed absolute "overbought" or "oversold" thresholds across different assets or price levels.

## 7. Best Practices

- **Trade in Direction of Zero Line Regime:** Only take bullish Signal Line crossovers when the MACD Line is above zero (or turning up from deep oversold territory), and only take bearish crossovers when below zero.
- **Watch Histogram Peak Shifts:** Look for histogram slope changes (e.g., dark green to light green) to exit trades early rather than waiting for full line crossovers.
- **Combine with Key Support/Resistance:** Validate MACD divergence or crossovers only when price arrives at major structural support, resistance, or supply/demand zones.

## 8. Common Mistakes

- **Treating MACD as Bounded Overbought/Oversold:** Expecting a specific numerical MACD height to cap price, ignoring that MACD can expand endlessly during strong trends.
- **Trading Every Signal Line Crossover:** Blindly executing trades on every cross in low-volatility or sideways markets, leading to severe decay from transaction costs and slippage.
- **Ignoring the Zero Line Context:** Taking counter-trend buy signals while the MACD is deep beneath the zero line without additional structural reversal triggers.

## 9. Related Strategies

- MACD Zero-Line Regime Trend Strategy
- MACD Histogram Momentum Divergence Setup
- MACD + RSI Dual Confirmation System

## 10. Related Concepts

- [[EMA.md]]
- [[RSI.md]]
- [[TrendAnalysis.md]]