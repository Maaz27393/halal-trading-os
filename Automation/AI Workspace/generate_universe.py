import os
import pandas as pd
import json

# Update with your actual file path (e.g., your saved Excel path)
excel_path = r"D:\Updated Halal Stocks-June 2026.xlsx" 
output_json_path = r"D:\OBSIDIAN VAULT\halal-trading-os\Automation\AI Workspace\Canonical Universe\halal_universe_177.json"

if not os.path.exists(excel_path):
    raise FileNotFoundError(f"Excel file not found at {excel_path}. Please verify the path.")

# Read from the 'Watchlist' sheet as per the new file structure
xls = pd.ExcelFile(excel_path)
df = pd.read_excel(excel_path, sheet_name="Watchlist")

# Clean column headers
df.columns = [str(c).replace("\xa0", " ").strip() for c in df.columns]

# Extract clean symbols
symbols = df["Symbol"].dropna().astype(str).str.strip().str.upper().drop_duplicates().tolist()

universe_data = {
  "universe_name": "Updated Watchlist 2026",
  "source_rows": len(df),
  "unique_compliant_symbols": len(symbols),
  "symbols": symbols
}

os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(universe_data, f, indent=2, ensure_ascii=False)

print(f"Successfully generated canonical JSON with {len(symbols)} unique symbols at: {output_json_path}")