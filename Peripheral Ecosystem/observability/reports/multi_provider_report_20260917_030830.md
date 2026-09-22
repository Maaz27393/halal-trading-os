# Halal Trading OS - Multi-Provider Orchestration Report

Generated: 2026-09-17 03:12:34

## Governance

- READ_ONLY: TRUE
- LIVE_AUTO_EXECUTION: FALSE
- ORDER_CAPABILITY: NONE
- EXECUTION_AUTHORITY: NONE

## Qwen Synthesis

### Pre-Market Cross-Source Report  

#### 1. **Broad Market Condition (NSE)**  
- **Market Status**: Open (NIFTY 50 and NIFTY50 USD active).  
- **Market Cap**: ₹47.229 crore (as of 16-Sep-2026).  
- **Nifty 50 Index**: Closed (`indicativenifty50: "CLOSE"`).  
- **Nifty Futures (FUTIDX)**: Last price = 23,126 (down 141 points, -0.61% day change).  
- **Breadth**: 4,803 advances, 4,700 declines, 116 unchanged.  

#### 2. **India VIX and Breadth**  
- **India VIX**: *Not available* (only index name provided; no numerical value).  
- **Breadth**: Confirmed via NSE (`advance_decline`): 4,803 advances, 4,700 declines, 116 unchanged.  

#### 3. **Chartink Candidate Symbols and Scanner Attribution**  
- **Candidate Count**: 0 (empty list).  
- **Scanner Attribution**: No symbols identified (Chartink scanner returned no results).  

#### 4. **Screener Fundamental Availability**  
- **Fundamentals**: *Not available* (empty `profiles` list).  

#### 5. **Relevant Vault Rules/Context**  
- **Active Rules**:  
  - Entry Rules (score: 214)  
  - Position Sizing (score: 214)  
  - Risk Management (score: 212)  
- **Active Strategies**:  
  - Breakout (score: 231)  
  - EMA20-50 Pullback (score: 215)  
- **Key Supporting Document**:  
  - Daily Pre-Market SOP (score: 197)  
- **Vault Status**: 91 files loaded (no skips).  

#### 6. **Cross-Source Observations**  
- NSE provides robust market cap, breadth, and futures data but Nifty 50 index is closed (`CLOSE` status).  
- Chartink and Screener both returned **empty results** (0 candidates, no profiles), indicating no actionable fundamentals or symbols for immediate analysis.  
- Vault rules confirm strict adherence to pre-market protocols (Daily Pre-Market SOP) and risk/position frameworks.  
- **Critical Note**: Nifty 50 index closure (`CLOSE`) may indicate end-of-day settlement; trading activity is likely ongoing per market state.  

#### 7. **Explicit Data Limitations**  
| **Source**       | **Limitation**                                                                 |
|-------------------|------------------------------------------------------------------------------|
| **India VIX**     | Numerical value unavailable (only index name provided).                        |
| **Chartink**      | 0 candidate symbols found (scanner inactive for pre-market).                   |
| **Screener**      | No fundamental profiles available (empty dataset).                             |
| **NSE (Nifty 50)**| Index status marked `CLOSE` (may imply end-of-day settlement; not live for trading). |

---  
**Report Compliance**: All outputs strictly adhere to `READ_ONLY = true`, `LIVE_AUTO_EXECUTION = false`, `ORDER_CAPABILITY = NONE`, and `EXECUTION_AUTHORITY = NONE` constraints. No execution or external actions were initiated.  
**Final Note**: Pre-market analysis requires manual review of NSE index status and vault rules due to data gaps (India VIX, Chartink, Screener). Proceed with caution per Vault’s Daily Pre-Market SOP.
