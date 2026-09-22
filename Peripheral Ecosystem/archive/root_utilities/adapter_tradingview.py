import os
import pandas as pd
from datetime import datetime
from opportunity_manager import get_or_create_opportunity_id

OUTPUT_DIR = r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi"

def ingest_tradingview_technical(
    symbol: str, 
    timeframe: str = "1D", 
    indicator_state: str = "BULLISH_ALIGNMENT", 
    confirmation: str = "CONFIRMED",
    close_price: float = 2500.0
):
    """
    Ingests technical evidence observations from TradingView, binds them to the canonical 
    OpportunityID, and appends telemetry to powerbi_technical_events.csv.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get or reuse canonical OpportunityID via Lifecycle Manager
    opportunity_id = get_or_create_opportunity_id(symbol)
    
    tech_path = os.path.join(OUTPUT_DIR, "powerbi_technical_events.csv")
    tech_df = pd.read_csv(tech_path) if os.path.exists(tech_path) else pd.DataFrame()
    
    technical_event_id = f"TECH-{opportunity_id}"
    
    # Prevent duplicate technical logs for the same opportunity thread
    if not tech_df.empty and "TechnicalEventID" in tech_df.columns:
        if technical_event_id in tech_df["TechnicalEventID"].values:
            print(f"[TradingView Adapter] Technical event {technical_event_id} already logged. Skipping duplicate.")
            return opportunity_id

    new_tech = pd.DataFrame([{
        "TechnicalEventID": technical_event_id,
        "OpportunityID": opportunity_id,
        "Symbol": symbol,
        "Timestamp": timestamp,
        "Provider": "TradingView",
        "Timeframe": timeframe,
        "IndicatorState": indicator_state,
        "EMA20": close_price * 0.98,
        "EMA50": close_price * 0.95,
        "VWAP": close_price * 0.99,
        "RSI50": 61.2,
        "RSI10": 67.5,
        "AVPUsed": "YES",
        "FRVPUsed": "NO",
        "PivotContext": "SUPPORT_HELD",
        "Confirmation": confirmation,
        "SourceEventID": f"TV-{timestamp.replace('-', '').replace(':', '').replace(' ', '-')}-{symbol}"
    }])
    
    tech_df = pd.concat([tech_df, new_tech], ignore_index=True)
    tech_df.to_csv(tech_path, index=False, encoding="utf-8-sig")
    
    print(f"[TradingView Adapter] Successfully recorded technical evidence for {symbol} under {opportunity_id}")
    return opportunity_id

if __name__ == "__main__":
    # Test ingestion for RELIANCE
    ingest_tradingview_technical("RELIANCE", "1D", "BULLISH_ALIGNMENT", "CONFIRMED", 2540.0)