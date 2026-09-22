import os
import pandas as pd
from datetime import datetime

OUTPUT_DIR = r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi"

def get_or_create_opportunity_id(symbol: str, scan_date: str = None) -> str:
    """
    Deterministic OpportunityID lifecycle manager.
    Checks existing event feeders to see if an active opportunity for this Symbol 
    already exists on the given date. If so, reuses it. Otherwise, generates 
    the next sequential OPP-YYYYMMDD-NNNN identifier.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not scan_date:
        scan_date = datetime.now().strftime("%Y%m%d")
    else:
        scan_date = scan_date.replace("-", "")

    scanner_path = os.path.join(OUTPUT_DIR, "powerbi_scanner_events.csv")
    
    # Check if file exists and has records
    existing_opps = []
    if os.path.exists(scanner_path):
        df = pd.read_csv(scanner_path)
        if not df.empty and "OpportunityID" in df.columns and "Symbol" in df.columns:
            # Filter for the same symbol and date prefix
            date_prefix = f"OPP-{scan_date}-"
            match = df[(df["Symbol"] == symbol) & (df["OpportunityID"].str.startswith(date_prefix))]
            if not match.empty:
                # Reuse the existing OpportunityID for this session/day
                existing_id = match.iloc[0]["OpportunityID"]
                print(f"[Lifecycle Manager] Reusing existing OpportunityID: {existing_id} for {symbol}")
                return existing_id
            
            # Count total for sequence generation on this date
            all_date_opps = df[df["OpportunityID"].str.startswith(date_prefix)]
            seq_num = len(all_date_opps) + 1
        else:
            seq_num = 1
    else:
        seq_num = 1

    new_opp_id = f"OPP-{scan_date}-{seq_num:03d}"
    print(f"[Lifecycle Manager] Generated new OpportunityID: {new_opp_id} for {symbol}")
    return new_opp_id

if __name__ == "__main__":
    # Test execution
    test_id = get_or_create_opportunity_id("RELIANCE")
    print(f"Test Result ID: {test_id}")