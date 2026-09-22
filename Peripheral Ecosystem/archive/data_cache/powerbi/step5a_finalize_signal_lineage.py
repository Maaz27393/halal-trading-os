import os
import pandas as pd

# ============================================================
# STEP 5A
# Finalize powerbi_signals.csv
# Create powerbi_signal_trade_bridge.csv
#
# Safe rules:
# - Preserve existing signal records
# - Do not invent SignalID -> TradeID relationships
# - Do not modify Fact_Trades
# - Do not modify the frozen Trading OS core
# ============================================================

BASE_DIR = r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi"

SIGNALS_FILE = os.path.join(
    BASE_DIR,
    "powerbi_signals.csv"
)

TRADES_FILE = os.path.join(
    BASE_DIR,
    "powerbi_trades.csv"
)

BRIDGE_FILE = os.path.join(
    BASE_DIR,
    "powerbi_signal_trade_bridge.csv"
)

# ------------------------------------------------------------
# Existing feeder contract
# ------------------------------------------------------------

BASE_SIGNAL_COLUMNS = [
    "SignalID",
    "SignalTimestamp",
    "Symbol",
    "Provider",
    "SignalType",
    "Strategy",
    "Direction",
    "EntryPrice",
    "StopLoss",
    "Target",
    "RiskReward",
    "MarketRegime",
    "Shariah_Compliant",
    "Status",
    "Confidence",
    "SourceEventID",
]

# Additional lifecycle fields.
# These are additive only.
EXTENDED_SIGNAL_COLUMNS = [
    "Shariah_Status",
    "Risk_Status",
    "Pipeline_Stage",
]

FINAL_SIGNAL_COLUMNS = (
    BASE_SIGNAL_COLUMNS +
    EXTENDED_SIGNAL_COLUMNS
)

# ------------------------------------------------------------
# Bridge contract
# ------------------------------------------------------------

BRIDGE_COLUMNS = [
    "BridgeID",
    "SignalID",
    "TradeID",
    "LinkType",
    "Rejection_Reason",
    "LinkTimestamp",
]

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def fail(message):
    raise RuntimeError(message)


def ensure_file_exists(path, label):
    if not os.path.exists(path):
        fail(f"{label} not found:\n{path}")


# ------------------------------------------------------------
# 1. Validate source files
# ------------------------------------------------------------

ensure_file_exists(
    SIGNALS_FILE,
    "powerbi_signals.csv"
)

ensure_file_exists(
    TRADES_FILE,
    "powerbi_trades.csv"
)

print("=" * 78)
print("STEP 5A — POWER BI SIGNAL LINEAGE PREPARATION")
print("=" * 78)
print()
print(f"Signals : {SIGNALS_FILE}")
print(f"Trades  : {TRADES_FILE}")
print(f"Bridge  : {BRIDGE_FILE}")
print()

# ------------------------------------------------------------
# 2. Load signals
# ------------------------------------------------------------

signals = pd.read_csv(
    SIGNALS_FILE,
    dtype=str,
    keep_default_na=False
)

print(f"Existing signal rows: {len(signals)}")

# ------------------------------------------------------------
# 3. Validate existing required columns
# ------------------------------------------------------------

missing_base = [
    col
    for col in BASE_SIGNAL_COLUMNS
    if col not in signals.columns
]

if missing_base:
    fail(
        "powerbi_signals.csv is missing required columns:\n"
        + "\n".join(f"  - {c}" for c in missing_base)
    )

# ------------------------------------------------------------
# 4. Add lifecycle columns only if absent
# ------------------------------------------------------------

for column in EXTENDED_SIGNAL_COLUMNS:
    if column not in signals.columns:
        signals[column] = ""

# ------------------------------------------------------------
# 5. Normalize text fields
# ------------------------------------------------------------

for column in FINAL_SIGNAL_COLUMNS:
    signals[column] = (
        signals[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )

# ------------------------------------------------------------
# 6. Validate SignalID
# ------------------------------------------------------------

if (signals["SignalID"] == "").any():
    bad_count = int((signals["SignalID"] == "").sum())

    fail(
        f"{bad_count} signal record(s) have an empty SignalID."
    )

duplicates = signals.loc[
    signals["SignalID"].duplicated(keep=False),
    "SignalID"
].tolist()

if duplicates:
    fail(
        "Duplicate SignalID values detected:\n"
        + "\n".join(
            f"  - {x}"
            for x in sorted(set(duplicates))
        )
    )

# ------------------------------------------------------------
# 7. Normalize status fields where possible
# ------------------------------------------------------------

signals["Shariah_Status"] = signals["Shariah_Status"].replace({
    "Yes": "PASS",
    "YES": "PASS",
    "yes": "PASS",
    "No": "FAIL",
    "NO": "FAIL",
    "no": "FAIL",
})

# If the original Shariah_Compliant field contains a value,
# use it only to populate an empty Shariah_Status.
empty_shariah = signals["Shariah_Status"] == ""

signals.loc[
    empty_shariah &
    signals["Shariah_Compliant"].str.upper().eq("YES"),
    "Shariah_Status"
] = "PASS"

signals.loc[
    empty_shariah &
    signals["Shariah_Compliant"].str.upper().eq("NO"),
    "Shariah_Status"
] = "FAIL"

# Existing status is not automatically treated as Risk_Status.
# We leave Risk_Status blank until a real governance/risk event
# supplies an authoritative result.
#
# This prevents us from inventing risk outcomes.

# ------------------------------------------------------------
# 8. Derive Pipeline_Stage only from explicit Status values
# ------------------------------------------------------------

status_upper = signals["Status"].str.upper()

stage_map = {
    "EXECUTED": "Executed",
    "TRADED": "Executed",
    "CANDIDATE": "Candidate",
    "REJECTED": "Rejected",
    "FAILED": "Rejected",
    "PASS": "Candidate",
}

empty_stage = signals["Pipeline_Stage"] == ""

for status_value, stage_value in stage_map.items():
    signals.loc[
        empty_stage & status_upper.eq(status_value),
        "Pipeline_Stage"
    ] = stage_value

# ------------------------------------------------------------
# 9. Preserve final schema/order
# ------------------------------------------------------------

signals = signals[FINAL_SIGNAL_COLUMNS]

# ------------------------------------------------------------
# 10. Save finalized signals
# ------------------------------------------------------------

signals.to_csv(
    SIGNALS_FILE,
    index=False,
    encoding="utf-8-sig"
)

print()
print("SIGNAL FEEDER")
print("-" * 78)
print(f"Rows saved    : {len(signals)}")
print(f"Columns saved : {len(signals.columns)}")
print()

for column in signals.columns:
    print(f"  {column}")

# ------------------------------------------------------------
# 11. Load trades
# ------------------------------------------------------------

trades = pd.read_csv(
    TRADES_FILE,
    dtype=str,
    keep_default_na=False
)

if "TradeID" not in trades.columns:
    fail(
        "powerbi_trades.csv does not contain TradeID."
    )

trades["TradeID"] = (
    trades["TradeID"]
    .fillna("")
    .astype(str)
    .str.strip()
)

if (trades["TradeID"] == "").any():
    fail(
        "powerbi_trades.csv contains an empty TradeID."
    )

trade_duplicates = trades.loc[
    trades["TradeID"].duplicated(keep=False),
    "TradeID"
].tolist()

if trade_duplicates:
    fail(
        "Duplicate TradeID values detected:\n"
        + "\n".join(
            f"  - {x}"
            for x in sorted(set(trade_duplicates))
        )
    )

# ------------------------------------------------------------
# 12. Create bridge
# ------------------------------------------------------------
#
# IMPORTANT:
# We do NOT automatically match SignalID to TradeID.
# There is currently no authoritative lineage field in the
# historical trade export proving such a relationship.
#
# Therefore the bridge is intentionally created empty.
# Real relationships will be appended only when the operational
# pipeline provides explicit lineage.

bridge = pd.DataFrame(
    columns=BRIDGE_COLUMNS
)

bridge.to_csv(
    BRIDGE_FILE,
    index=False,
    encoding="utf-8-sig"
)

# ------------------------------------------------------------
# 13. Verification
# ------------------------------------------------------------

print()
print("BRIDGE")
print("-" * 78)
print("Bridge rows   :", len(bridge))
print("Bridge columns:", len(bridge.columns))
print()

for column in bridge.columns:
    print(f"  {column}")

# ------------------------------------------------------------
# 14. Current lineage status
# ------------------------------------------------------------

signal_ids = set(signals["SignalID"])
trade_ids = set(trades["TradeID"])

potential_same_id = sorted(
    signal_ids.intersection(trade_ids)
)

print()
print("LINEAGE CHECK")
print("-" * 78)
print(f"Unique SignalID values : {len(signal_ids)}")
print(f"Unique TradeID values  : {len(trade_ids)}")
print(
    f"Same-ID overlaps       : {len(potential_same_id)}"
)

if potential_same_id:
    print()
    print(
        "NOTICE: The following identifiers exist in both "
        "SignalID and TradeID:"
    )

    for value in potential_same_id:
        print(f"  - {value}")

    print()
    print(
        "They were NOT linked automatically because identical "
        "text does not prove signal-to-trade lineage."
    )
else:
    print(
        "No SignalID/TradeID overlap detected."
    )

# ------------------------------------------------------------
# 15. Governance verification
# ------------------------------------------------------------

print()
print("GOVERNANCE")
print("-" * 78)
print("Power BI layer:")
print("  READ_ONLY = True")
print("  LIVE_AUTO_EXECUTION = False")
print("  ORDER_CAPABILITY = NONE")
print("  EXECUTION_AUTHORITY = NONE")

print()
print("=" * 78)
print("STEP 5A COMPLETE")
print("=" * 78)
print()
print("Final signal file:")
print(SIGNALS_FILE)
print()
print("Bridge file:")
print(BRIDGE_FILE)
print()
print(
    "No existing trade records, provider adapters, or frozen "
    "Trading OS components were modified."
)
