import os
import pandas as pd
from datetime import datetime
from opportunity_manager import get_or_create_opportunity_id

OUTPUT_DIR = r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi"

def ingest_chartink_signal(symbol: str, scanner_name: str, signal_type: str, scanner_value: str = "1"):
    """
    Ingests a Chartink scanner trigger event, obtains/reuses the canonical OpportunityID,
    and appends the telemetry to powerbi_scanner_events.csv with full provenance.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get or reuse canonical OpportunityID via Lifecycle Manager
    opportunity_id = get_or_create_opportunity_id(symbol)
    
    scanner_path = os.path.join(OUTPUT_DIR, "powerbi_scanner_events.csv")
    scanner_df = pd.read_csv(scanner_path) if os.path.exists(scanner_path) else pd.DataFrame()
    
    scanner_event_id = f"SCN-{opportunity_id}"
    
    # Check if this exact scanner event already exists for this opportunity
    if not scanner_df.empty and "ScannerEventID" in scanner_df.columns:
        if scanner_event_id in scanner_df["ScannerEventID"].values:
            print(f"[Chartink Adapter] Scanner event {scanner_event_id} already logged. Skipping duplicate.")
            return opportunity_id

    new_event = pd.DataFrame([{
        "ScannerEventID": scanner_event_id,
        "OpportunityID": opportunity_id,
        "Symbol": symbol,
        "ScanTimestamp": timestamp,
        "Provider": "Chartink",
        "ScannerName": scanner_name,
        "SignalType": signal_type,
        "ScannerStatus": "ACTIVE",
        "ScannerValue": scanner_value,
        "SourceEventID": f"SRC-{timestamp.replace('-', '').replace(':', '').replace(' ', '-')}-{symbol}"
    }] )
    
    scanner_df = pd.concat([scanner_df, new_event], ignore_index=True)
    scanner_df.to_csv(scanner_path, index=False, encoding="utf-8-sig")
    
    print(f"[Chartink Adapter] Successfully recorded scanner event for {symbol} under {opportunity_id}")
    return opportunity_id

if __name__ == "__main__":
    # Test ingestion
    ingest_chartink_signal("RELIANCE", "Volume Breakout 20D", "BREAKOUT")