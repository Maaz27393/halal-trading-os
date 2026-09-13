from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class BaseCanonicalModel(BaseModel):
    """Base abstract model for all canonical peripheral data contracts."""
    source_provider: str
    ingested_at: datetime = Field(default_factory=datetime.utcnow)

class MarketData(BaseCanonicalModel):
    """Canonical representation of market ticker data."""
    symbol: str
    price: float
    volume: Optional[int] = None

class MarketQuote(BaseCanonicalModel):
    """Canonical representation of an equity or instrument market quote."""
    symbol: str
    exchange: str = "NSE"
    last_price: float
    change_percent: float
    volume: int
    bid: Optional[float] = None
    ask: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class FundamentalData(BaseCanonicalModel):
    """Canonical representation of company fundamentals."""
    symbol: str
    roe: Optional[float] = None
    pe_ratio: Optional[float] = None

class FundamentalMetric(BaseCanonicalModel):
    """Canonical representation of company fundamentals (e.g., Screener metrics)."""
    symbol: str
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)

class NewsItem(BaseCanonicalModel):
    title: str
    summary: str

class EarningsEvent(BaseCanonicalModel):
    symbol: str
    date: str

class TradingSignal(BaseCanonicalModel):
    symbol: str
    signal_type: str

class ResearchDocument(BaseCanonicalModel):
    title: str
    content: str

class KnowledgeItem(BaseCanonicalModel):
    chunk_id: str
    parent_document_uri: str
    content: str
    embedding_model: str
    vector_dimension: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowResult(BaseCanonicalModel):
    workflow_id: str
    status: str
    output: Dict[str, Any]

class ScanResult(BaseCanonicalModel):
    """Canonical representation of technical scanner output (e.g., Chartink)."""
    scanner_name: str
    matched_symbols: List[str] = Field(default_factory=list)
    raw_results: List[Dict[str, Any]] = Field(default_factory=list)

class MacroIndicator(BaseCanonicalModel):
    """Canonical representation of macroeconomic indicators (inflation, interest rates, GDP, etc.)."""
    indicator_name: str
    value: float
    unit: str = "%"
    period: str = "Current"
    country: str = "India"

from enum import Enum

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL_M = "SL-M"
    SL_L = "SL-L"

class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class ProductType(str, Enum):
    CNC = "CNC"
    MIS = "MIS"
    NRML = "NRML"

class ExecutionIntent(BaseCanonicalModel):
    """Canonical structure representing a strategy's raw execution request."""
    strategy_id: str
    symbol: str
    exchange: str = "NSE"
    transaction_type: TransactionType
    order_type: OrderType
    product: ProductType = ProductType.MIS
    quantity: int
    price: float = 0.0
    trigger_price: float = 0.0
    stop_loss: float = 0.0
    target: float = 0.0
    idempotency_key: str

class OrderResponse(BaseCanonicalModel):
    """Canonical structure representing the broker's response to an order dispatch."""
    broker_order_id: Optional[str] = None
    status: str  # REJECTED, PENDING, COMPLETE, OPEN
    message: str = ""
    filled_quantity: int = 0
    average_price: float = 0.0