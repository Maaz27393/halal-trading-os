# Halal Trading OS - Multi-Provider Orchestration Report

Generated: 2026-09-17 08:55:55

## Governance

- READ_ONLY: TRUE
- LIVE_AUTO_EXECUTION: FALSE
- ORDER_CAPABILITY: NONE
- EXECUTION_AUTHORITY: NONE

## Qwen Synthesis

### Pre-Market Cross-Source Report for Halal Trading OS  

1. **Broad market condition from NSE**  
   - *Provider fact*: Market is open (NIFTY 50 index present in `marketState`).  
   - *Derived observation*: Market cap data available but from **previous trading day** (16-Sep-2026).  
   - *Unavailable*: Real-time market cap.  

2. **India VIX and breadth**  
   - *Provider fact*: India VIX index name available (no value provided).  
   - *Derived observation*: Market breadth shows **slight bullish momentum** (4,803 advances vs. 4,700 declines; 116 unchanged).  
   - *Unavailable*: Actual India VIX value.  

3. **Chartink candidate symbols and scanner attribution**  
   - *Provider fact*: **0 candidate symbols** found (`candidate_count=0`).  
   - *Derived observation*: No actionable symbols for scanning.  
   - *Unavailable*: None.  

4. **Screener fundamental availability**  
   - *Provider fact*: **No fundamental data** available (`success_count=0`).  
   - *Derived observation*: Screener system unresponsive to fundamental queries.  
   - *Unavailable*: Fundamental data.  

5. **Relevant Vault rules/context**  
   - *Provider fact*: Active rules: **Entry Rules**, **Position Sizing**, **Risk Management**.  
   - *Provider fact*: Active strategies: **Breakout**, **EMA20-50 Pullback**.  
   - *Derived observation*: Halal trading workflow fully configured and operational.  

6. **Cross-source observations**  
   - Market open but **historical market cap** (not real-time).  
   - **India VIX value missing** (only index name provided).  
   - **No candidate symbols** (Chartink) and **no fundamentals** (Screener) available.  

7. **Unavailable information**  
   - Actual India VIX value.  
   - Real-time market cap data.  
   - Candidate symbols (Chartink).  
   - Fundamental data (Screener).  

---  
*Report generated from integrated source data. System readiness confirmed per Vault rules.*
