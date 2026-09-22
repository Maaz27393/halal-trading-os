import os
import zipfile

# ============================================================
# STEP 8C — READ-ONLY PBIX LEGACY SIGNAL MODEL AUDIT
# ============================================================

PBIX_PATH = r"D:\OBSIDIAN VAULT\Trading Reports.pbix"

SEARCH_TERMS = [
    "Fact_Signals",
    "Bridge_SignalTrade",
    "powerbi_signals.csv",
    "SignalID",
    "Total Signals",
    "Signals Linked to Trades",
    "Signal-to-Trade Conversion",
]

if not os.path.exists(PBIX_PATH):
    raise FileNotFoundError(
        f"PBIX file not found:\n{PBIX_PATH}"
    )

print("=" * 80)
print("STEP 8C — PBIX LEGACY SIGNAL MODEL AUDIT")
print("=" * 80)
print()
print("PBIX:", PBIX_PATH)
print()

with zipfile.ZipFile(PBIX_PATH, "r") as z:

    names = z.namelist()

    print("PBIX package opened successfully.")
    print(f"Package files: {len(names)}")
    print()

    # --------------------------------------------------------
    # Key package objects
    # --------------------------------------------------------

    print("Key package objects:")

    for name in [
        "Report/Layout",
        "DataModel",
        "DiagramLayout",
        "Settings",
    ]:
        print(
            f"  {name}: "
            f"{'FOUND' if name in names else 'NOT FOUND'}"
        )

    # --------------------------------------------------------
    # Search package contents
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("LEGACY / LINEAGE TERM SEARCH")
    print("=" * 80)

    found_any = False

    for filename in names:

        lower = filename.lower()

        # Skip obvious binary resources
        if any(
            lower.endswith(ext)
            for ext in (
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".ico",
                ".bmp",
                ".woff",
                ".woff2",
                ".ttf",
            )
        ):
            continue

        try:
            raw = z.read(filename)
        except Exception:
            continue

        text = raw.decode(
            "utf-8",
            errors="ignore"
        )

        text_lower = text.lower()

        matches = [
            term
            for term in SEARCH_TERMS
            if term.lower() in text_lower
        ]

        if matches:
            found_any = True

            print()
            print(filename)

            for term in matches:
                print(f"  FOUND: {term}")

    if not found_any:
        print("No searched terms found.")

    # --------------------------------------------------------
    # Report Layout
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("REPORT LAYOUT AUDIT")
    print("=" * 80)

    if "Report/Layout" in names:

        raw = z.read("Report/Layout")

        # PBIX Layout is normally UTF-16LE
        layout = raw.decode(
            "utf-16-le",
            errors="ignore"
        )

        for term in SEARCH_TERMS:

            count = layout.lower().count(
                term.lower()
            )

            print(
                f"{term:35} occurrences: {count}"
            )

    else:
        print("Report/Layout not found.")

    # --------------------------------------------------------
    # Diagram Layout
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("MODEL DIAGRAM AUDIT")
    print("=" * 80)

    if "DiagramLayout" in names:

        raw = z.read("DiagramLayout")

        diagram = raw.decode(
            "utf-8",
            errors="ignore"
        )

        for term in [
            "Fact_Signals",
            "Bridge_SignalTrade",
            "Fact_Trades",
            "Dim_Date",
            "Dim_Stocks",
            "Dim_Strategy",
            "Dim_Emotion",
        ]:

            count = diagram.lower().count(
                term.lower()
            )

            print(
                f"{term:35} occurrences: {count}"
            )

    else:
        print("DiagramLayout not found.")


print()
print("=" * 80)
print("STEP 8C COMPLETE")
print("=" * 80)
print()
print("READ-ONLY AUDIT")
print("NO PBIX CHANGES MADE")
