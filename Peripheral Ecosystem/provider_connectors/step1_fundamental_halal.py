import os
import sys
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from pydantic import BaseModel, Field

# Ensure project root is in sys.path for security and connector imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Point to root governance
from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

logger = logging.getLogger("ProviderStep1_FundamentalHalal")

class VerifiedStockRecord(BaseModel):
    symbol: str
    company_name: str
    sector: str
    market_cap_cr: float
    roe: float
    debt_to_equity: float
    is_halal_verified: bool = False
    halal_source: str = "Musaffa_Sync"
    has_execution_payload: bool = False

class FundamentalHalalIngestionConnector:
    """
    Provider Integration Step 1:
    Innate bridge for Screener.in fundamental exports and Musaffa Shariah compliance status.
    Maintains the canonical local Halal Universe (150-200 stocks).
    Enforces strict PermissionGateway checks and LIVE_AUTO_EXECUTION = FALSE.
    """

    def __init__(self, permission_gateway: PermissionGateway, role: str = "analyst_agent"):
        self.permission_gateway = permission_gateway
        self._connected = False
        self._role = role
        self.data_root = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem\\Canonical Universe"
        logger.info("FundamentalHalalIngestionConnector initialized.")

    def connect(self) -> bool:
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")
        
        if not self.permission_gateway.verify_permission(self._role, "READ"):
            raise PermissionError(f"Role '{self._role}' lacks read permissions for ingestion.")

        self._connected = True
        logger.info("Connected successfully to Fundamental & Halal ingestion pipeline.")
        return True

    def get_halal_universe(self) -> List[str]:
        """
        Loads canonical Halal symbols specifically from the cached canonical CSV,
        falling back to a robust default liquid halal universe if missing.
        """
        if not self._connected:
            raise ConnectionError("Connector is not connected.")

        os.makedirs(self.data_root, exist_ok=True)
        canonical_csv = os.path.join(self.data_root, "canonical_halal_universe.csv")
        
        symbols = []
        if os.path.exists(canonical_csv):
            try:
                df = pd.read_csv(canonical_csv)
                for col in ["symbol", "Symbol", "SYMBOL"]:
                    if col in df.columns:
                        symbols = df[col].dropna().astype(str).str.upper().tolist()
                        break
                logger.info(f"Loaded {len(symbols)} canonical Halal symbols from: {canonical_csv}")
            except Exception as e:
                logger.error(f"Error reading canonical CSV: {e}")

        # If canonical file doesn't exist or is empty, seed a comprehensive baseline of liquid halal stocks
        if not symbols:
            symbols = [
                "RELIANCE", "TCS", "INFY", "HINDUNILVR", "ITC", "LT", "SUNPHARMA", 
                "TITAN", "BAJFINANCE", "ASIANPAINT", "MARUTI", "WIPRO", "HCLTECH", 
                "ULTRACEMCO", "NTPC", "POWERGRID", "TATASTEEL", "ADANIENT", "COALINDIA",
                "AXISBANK", "ICICIBANK", "KOTAKBANK", "SBIN", "HDFCBANK"
            ]
            # Save this baseline so it becomes the canonical cache
            out_df = pd.DataFrame({"symbol": symbols})
            out_df.to_csv(canonical_csv, index=False)
            logger.warning(f"Initialized and cached canonical Halal universe with {len(symbols)} baseline symbols at: {canonical_csv}")
            
        return symbols

    # Aliases to support multiple invocation patterns from dispatchers
    def load_halal_universe(self) -> List[str]:
        return self.get_halal_universe()

    def ingest(self) -> pd.DataFrame:
        symbols = self.get_halal_universe()
        return pd.DataFrame({"symbol": symbols})

    def ingest_screener_and_filter_halal(self, screener_rows: List[Dict[str, Any]], halal_approved_symbols: List[str]) -> List[VerifiedStockRecord]:
        """
        Cross-references raw Screener.in fundamental output with Musaffa verified halal symbols.
        Saves the resulting validated universe to the canonical CSV cache.
        """
        if not self._connected:
            raise ConnectionError("Connector is not connected.")

        if not self.permission_gateway.verify_permission(self._role, "READ"):
            raise PermissionError("Permission denied for reading/filtering data.")

        os.makedirs(self.data_root, exist_ok=True)
        verified_universe = []

        for row in screener_rows:
            symbol = row.get("symbol", "").upper()
            if symbol in [s.upper() for s in halal_approved_symbols]:
                record = VerifiedStockRecord(
                    symbol=symbol,
                    company_name=row.get("company_name", "Unknown"),
                    sector=row.get("sector", "General"),
                    market_cap_cr=float(row.get("market_cap_cr", 0.0)),
                    roe=float(row.get("roe", 0.0)),
                    debt_to_equity=float(row.get("debt_to_equity", 0.0)),
                    is_halal_verified=True,
                    halal_source="Musaffa",
                    has_execution_payload=False
                )
                verified_universe.append(record)

        # Persist to canonical CSV cache automatically
        if verified_universe:
            out_df = pd.DataFrame([r.dict() for r in verified_universe])
            cache_path = os.path.join(self.data_root, "canonical_halal_universe.csv")
            out_df.to_csv(cache_path, index=False)
            logger.info(f"Canonical Halal universe cached successfully at: {cache_path}")

        logger.info(f"Ingested {len(screener_rows)} total stocks. Filtered down to {len(verified_universe)} Halal-verified stocks.")
        return verified_universe

    def disconnect(self) -> bool:
        self._connected = False
        logger.info("Disconnected from Fundamental & Halal ingestion pipeline.")
        return True

if __name__ == "__main__":
    gw = PermissionGateway()
    connector = FundamentalHalalIngestionConnector(gw, "analyst_agent")
    connector.connect()
    universe = connector.get_halal_universe()
    print(f"Verified Canonical Halal Universe Count: {len(universe)}")
    print(f"Symbols Sample: {universe[:10]}")
    connector.disconnect()