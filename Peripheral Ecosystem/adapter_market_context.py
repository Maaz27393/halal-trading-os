import os
import pandas as pd
from datetime import datetime
from opportunity_manager import get_or_create_opportunity_id

OUTPUT_DIR = r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi"

def ingest_market_context(
    symbol: str, 
    nifty_trend: str = "BULLISH", 
    india_vix: float = 13.2, 
    market_regime: str = "TRENDING"
):
    """
    Ingests broader NSE market context snapshots, binds them to the canonical 
    OpportunityID, and appends telemetry to powerbi_market_context.csv.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get or reuse canonical OpportunityID via Lifecycle Manager
    opportunity_id = get_or_create_opportunity_id(symbol)
    
    mkt_path = os.path.join(OUTPUT_DIR, "powerbi_market_context.csv")
    mkt_df = pd.read_csv(mkt_path) if os.path.exists(mkt_path) else pd.DataFrame()
    
    market_snapshot_id = f"MKT-{opportunity_id}"
    
    # Prevent duplicate market context logs for the same opportunity thread
    if not mkt_df.empty and "MarketSnapshotID" in mkt_df.columns:
        if market_snapshot_id in mkt_df["MarketSnapshotID"].values:
            print(f"[Market Context Adapter] Snapshot {market_snapshot_id} already logged. Skipping duplicate.")
            return opportunity_id

    new_mkt = pd.DataFrame([{
        "MarketSnapshotID": market_snapshot_id,
        "OpportunityID": opportunity_id,
        "Timestamp": timestamp,
        "NiftyTrend": nifty_trend,
        "IndiaVIX": india_vix,
        "Advances": 1250,
        "Declines": 750,
        "MarketRegime": market_regime,
        "Source": "NSE"
    }])
    
    mkt_df = pd.concat([mkt_df, new_mkt], ignore_index=True)
    mkt_df.to_csv(mkt_path, index=False, encoding="utf-8-sig")
    
    print(f"[Market Context Adapter] Successfully recorded market context for {symbol} under {opportunity_id}")
    return opportunity_id

if __name__ == "__main__":
    # Test ingestion for RELIANCE
    ingest_market_context("RELIANCE", "BULLISH", 13.2, "TRENDING")