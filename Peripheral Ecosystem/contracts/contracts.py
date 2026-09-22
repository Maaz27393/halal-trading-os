from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class BaseCanonicalModel(BaseModel):
    """Base model enforcing universal metadata across all contracts."""
    contract_version: str = "1.0.0"
    source_provider: str = Field(..., description="Abstract identifier of the underlying provider (e.g., 'screener', 'nse')")
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    raw_payload_hash: Optional[str] = Field(None, description="Checksum of original raw payload for auditability")


class MarketData(BaseCanonicalModel):
    """Normalized real-time or historical market pricing data."""
    symbol: str = Field(..., description="Standardized ticker symbol (e.g., 'RELIANCE', 'TCS')")
    exchange: str = Field("NSE", description="Exchange identifier")
    timeframe: str = Field("1D", description="Bar interval (e.g., '1m', '1h', '1D')")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: int = 0
    open_interest: Optional[int] = None


class MarketQuote(BaseCanonicalModel):
    """Canonical representation of an equity or instrument market quote."""
    symbol: str = Field(..., description="Standardized ticker symbol")
    exchange: str = Field("NSE", description="Exchange identifier")
    last_price: float = 0.0
    change_percent: float = 0.0
    volume: int = 0
    bid: Optional[float] = None
    ask: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FundamentalData(BaseCanonicalModel):
    """Normalized company fundamental and financial metrics."""
    symbol: str
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    debt_to_equity: Optional[float] = None
    dividend_yield: Optional[float] = None
    eps: Optional[float] = None
    book_value: Optional[float] = None
    quarterly_results: List[Dict[str, Any]] = Field(default_factory=list)
    custom_metrics: Dict[str, Any] = Field(default_factory=dict)


class FundamentalMetric(BaseCanonicalModel):
    """Canonical representation of company fundamentals (e.g., Screener metrics)."""
    symbol: str
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class NewsItem(BaseCanonicalModel):
    """Normalized news feed item or corporate announcement."""
    headline: str
    summary: str
    url: Optional[str] = None
    symbols: List[str] = Field(default_factory=list, description="Tickers affected or mentioned")
    published_at: datetime = Field(default_factory=datetime.utcnow)
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0)
    tags: List[str] = Field(default_factory=list)


class EarningsEvent(BaseCanonicalModel):
    """Normalized corporate earnings report details."""
    symbol: str
    fiscal_quarter: str = Field(..., description="e.g., 'Q3FY26'")
    announcement_date: datetime = Field(default_factory=datetime.utcnow)
    revenue_actual: Optional[float] = None
    revenue_estimated: Optional[float] = None
    net_profit_actual: Optional[float] = None
    net_profit_estimated: Optional[float] = None
    eps_actual: Optional[float] = None
    eps_estimated: Optional[float] = None
    guidance_notes: Optional[str] = None


class TradingSignal(BaseCanonicalModel):
    """Normalized technical or algorithmic signal generated for research/analysis."""
    symbol: str
    strategy_name: str
    direction: str = Field(..., description="'BUY', 'SELL', or 'NEUTRAL'")
    confidence: float = Field(..., ge=0.0, le=1.0)
    trigger_price: float = 0.0
    stop_loss: Optional[float] = None
    target_price: Optional[float] = None
    indicators_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Indicator values at trigger (e.g., RSI, VWAP, EMA)")


class ResearchDocument(BaseCanonicalModel):
    """Normalized internal research note, thesis, or extracted article."""
    title: str
    author: Optional[str] = None
    content_format: str = Field("markdown", description="'markdown', 'pdf_text', or 'html'")
    body: str
    storage_uri: str = Field(..., description="Local path in Obsidian vault or local database")
    tags: List[str] = Field(default_factory=list)
    referenced_symbols: List[str] = Field(default_factory=list)


class KnowledgeItem(BaseCanonicalModel):
    """Normalized atomic chunk for local RAG storage."""
    chunk_id: str
    parent_document_uri: str
    content: str
    embedding_model: str
    vector_dimension: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowResult(BaseCanonicalModel):
    """Standardized execution output for agent workflows (P5)."""
    workflow_name: str
    status: str = Field(..., description="'SUCCESS', 'PARTIAL', or 'FAILED'")
    execution_duration_seconds: float = 0.0
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list, description="List of generated outputs, files, or signals")
    errors: List[str] = Field(default_factory=list)


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
