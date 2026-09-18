"""
shadow_daily_runner.py

Halal Trading OS
Shadow Daily Runner

Purpose:
    Run the current canonical halal universe through the shadow-validation
    pipeline without modifying the frozen Phase 1-12 trading core.

Current canonical universe:
    Updated Halal Stocks-June 2026
    source_rows = 177
    compliant_rows = 176
    dynamic_verification_rows = 1
    unique_compliant_symbols = 173

Safety:
    - SHADOW mode only
    - No broker authentication
    - No live order submission
    - No live order payload creation
    - No modification of Phase 1-12 modules
    - yfinance is used only as a shadow/research data provider
    - StrategyAnalysisSuite is the actual technical validator
"""

import json
import logging
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import yfinance as yf


# ============================================================================
# PATHS
# ============================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent

CANONICAL_UNIVERSE = (
    WORKSPACE_ROOT
    / "Canonical Universe"
    / "halal_universe_177.json"
)

STRATEGY_MODULE_PATH = (
    WORKSPACE_ROOT
    / "Agent Runtime"
    / "skills"
)

LOG_DIR = SCRIPT_DIR / "logs"
AUDIT_DIR = WORKSPACE_ROOT / "Canonical Universe"

LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# LOGGING
# ============================================================================

LOG_FILE = LOG_DIR / "shadow_daily_runner.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] ShadowDailyRunner: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("ShadowDailyRunner")


# ============================================================================
# LOCAL MODULE PATHS
# ============================================================================
#
# The runner is executed as:
#
#     python .\orchestrator\shadow_daily_runner.py
#
# Therefore sibling orchestrator modules are imported directly.
#
# Frozen modules are NOT modified.
# ============================================================================

sys.path.insert(0, str(WORKSPACE_ROOT))
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(STRATEGY_MODULE_PATH))


from provider_symbol_adapter import ProviderSymbolAdapter
from market_data_adapter import MarketDataAdapter
from live_readiness_auditor import LiveReadinessAuditor
from failure_stress_harness import FailureStressHarness
from shadow_execution_engine import ShadowExecutionEngine
from phase12_master_orchestrator import Phase12MasterOrchestrator

from strategy_analysis_suite import StrategyAnalysisSuite


# ============================================================================
# SHADOW ACCOUNT CONFIGURATION
# ============================================================================

ACCOUNT_EQUITY = 50_000.00
MAX_RISK_PER_TRADE = 500.00
MAX_TRADES_PER_DAY = 2

MAX_SLIPPAGE_PCT = 0.5
MIN_RR = 1.5

SYSTEM_MODE = "SHADOW"


# ============================================================================
# SHADOW-ONLY BROKER SESSION
# ============================================================================

class ShadowOnlyBrokerSession:
    """
    Explicitly local shadow-only session.

    This exists only because the frozen Phase 12 ShadowExecutionEngine
    requires a session object for its connectivity gate.

    This object:
        - does not authenticate
        - contains no credentials
        - does not contact a broker
        - cannot submit orders
        - cannot generate live broker payloads
    """

    def __init__(self):
        self.mode = "SHADOW_ONLY"
        self.broker_name = "SHADOW_SIMULATOR"

    def is_session_valid(self) -> bool:
        return True


# ============================================================================
# CANONICAL UNIVERSE
# ============================================================================

def load_canonical_universe() -> list:
    """
    Load and validate the current canonical universe.

    The symbol count is derived from the JSON metadata rather than
    hard-coded as 174.
    """

    if not CANONICAL_UNIVERSE.exists():
        raise FileNotFoundError(
            f"Canonical universe not found: {CANONICAL_UNIVERSE}"
        )

    with open(
        CANONICAL_UNIVERSE,
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(
            "CANONICAL_UNIVERSE_INVALID_FORMAT"
        )

    symbols = data.get("symbols", [])

    if not isinstance(symbols, list):
        raise ValueError(
            "CANONICAL_UNIVERSE_SYMBOLS_INVALID"
        )

    cleaned_symbols = []

    for symbol in symbols:

        symbol = str(symbol).strip()

        if not symbol:
            continue

        if symbol.lower() == "nan":
            continue

        cleaned_symbols.append(symbol)

    unique_symbols = list(
        dict.fromkeys(cleaned_symbols)
    )

    metadata_count = data.get(
        "unique_compliant_symbols"
    )

    if metadata_count is None:
        raise ValueError(
            "CANONICAL_UNIVERSE_MISSING_COUNT"
        )

    try:
        metadata_count = int(metadata_count)
    except (ValueError, TypeError):
        raise ValueError(
            "CANONICAL_UNIVERSE_INVALID_COUNT"
        )

    if len(unique_symbols) != metadata_count:

        raise ValueError(
            "CANONICAL_UNIVERSE_COUNT_MISMATCH: "
            f"metadata={metadata_count}, "
            f"actual={len(unique_symbols)}"
        )

    logger.info(
        "Canonical universe loaded: %s symbols",
        len(unique_symbols),
    )

    logger.info(
        "Universe name: %s",
        data.get("universe_name"),
    )

    logger.info(
        "Source rows: %s | Compliant rows: %s | "
        "Dynamic verification rows: %s",
        data.get("source_rows"),
        data.get("compliant_rows"),
        data.get("dynamic_verification_rows"),
    )

    return unique_symbols


# ============================================================================
# RSI
# ============================================================================

def calculate_rsi(
    series: pd.Series,
    period: int = 14,
) -> pd.Series:
    """
    Calculate RSI using exponential/Wilder-style smoothing.
    """

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False,
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False,
    ).mean()

    rs = avg_gain / avg_loss.replace(
        0,
        pd.NA,
    )

    return 100 - (
        100 / (1 + rs)
    )


# ============================================================================
# INDICATORS
# ============================================================================

def calculate_indicators(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate indicators required by StrategyAnalysisSuite.
    """

    data = df.copy()

    if data.empty:
        return data

    if isinstance(
        data.columns,
        pd.MultiIndex,
    ):
        data.columns = (
            data.columns
            .get_level_values(0)
        )

    required_columns = {
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    }

    missing = (
        required_columns
        - set(data.columns)
    )

    if missing:
        raise ValueError(
            "MISSING_MARKET_COLUMNS: "
            + str(sorted(missing))
        )

    data["EMA20"] = (
        data["Close"]
        .ewm(
            span=20,
            adjust=False,
        )
        .mean()
    )

    data["EMA50"] = (
        data["Close"]
        .ewm(
            span=50,
            adjust=False,
        )
        .mean()
    )

    data["RSI"] = calculate_rsi(
        data["Close"],
        14,
    )

    typical_price = (
        data["High"]
        + data["Low"]
        + data["Close"]
    ) / 3.0

    cumulative_pv = (
        typical_price
        * data["Volume"]
    ).cumsum()

    cumulative_volume = (
        data["Volume"]
        .cumsum()
    )

    data["VWAP"] = (
        cumulative_pv
        / cumulative_volume.replace(
            0,
            pd.NA,
        )
    )

    return data


# ============================================================================
# MARKET DATA
# ============================================================================

def fetch_market_data(
    provider_symbol: str,
) -> Tuple[
    Optional[pd.DataFrame],
    Optional[str],
]:
    """
    Fetch recent 15-minute market data from yfinance.

    yfinance is explicitly treated as a shadow/research provider.
    """

    try:

        ticker = yf.Ticker(
            provider_symbol
        )

        df = ticker.history(
            period="5d",
            interval="15m",
            auto_adjust=False,
            prepost=False,
        )

        if df is None or df.empty:

            return (
                None,
                "PROVIDER_DATA_UNAVAILABLE",
            )

        return (
            df,
            None,
        )

    except Exception as exc:

        logger.warning(
            "%s provider error: %s",
            provider_symbol,
            exc,
        )

        return (
            None,
            "TEMPORARY_PROVIDER_ERROR",
        )


# ============================================================================
# MARKET SNAPSHOT
# ============================================================================

def get_latest_snapshot(
    canonical_symbol: str,
    provider_symbol: str,
    df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Calculate the latest validated market snapshot.
    """

    if df is None or df.empty:
        raise ValueError(
            "EMPTY_MARKET_DATA"
        )

    data = calculate_indicators(
        df
    )

    if data.empty:
        raise ValueError(
            "EMPTY_INDICATOR_DATA"
        )

    latest = data.iloc[-1]

    close_price = float(
        latest["Close"]
    )

    ema20 = float(
        latest["EMA20"]
    )

    ema50 = float(
        latest["EMA50"]
    )

    rsi = float(
        latest["RSI"]
    )

    vwap = float(
        latest["VWAP"]
    )

    if not all(
        math.isfinite(value)
        for value in (
            close_price,
            ema20,
            ema50,
            rsi,
            vwap,
        )
    ):
        raise ValueError(
            "INVALID_INDICATOR_VALUES"
        )

    timestamp = (
        latest.name.isoformat()
        if hasattr(
            latest.name,
            "isoformat",
        )
        else str(latest.name)
    )

    return {
        "canonical_symbol": canonical_symbol,
        "provider_symbol": provider_symbol,
        "ticker": canonical_symbol,

        "open": float(
            latest["Open"]
        ),

        "high": float(
            latest["High"]
        ),

        "low": float(
            latest["Low"]
        ),

        "close": close_price,

        "volume": int(
            latest["Volume"]
        ),

        "ema20": ema20,
        "ema50": ema50,
        "rsi": rsi,
        "vwap": vwap,

        "timestamp": timestamp,
    }


# ============================================================================
# SHADOW RISK PARAMETERS
# ============================================================================

def build_shadow_trade_parameters(
    snapshot: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Build a complete risk payload for shadow validation.

    IMPORTANT:

    The latest candle low is used only to construct a complete shadow
    risk payload. This does NOT change the frozen production strategy
    or establish a new production stop-loss rule.

    StrategyAnalysisSuite remains authoritative for setup validation.
    """

    entry = float(
        snapshot["close"]
    )

    candle_low = float(
        snapshot["low"]
    )

    if entry <= 0:
        return None

    if candle_low <= 0:
        return None

    if candle_low >= entry:
        return None

    risk_per_share = (
        entry - candle_low
    )

    if risk_per_share <= 0:
        return None

    quantity = math.floor(
        MAX_RISK_PER_TRADE
        / risk_per_share
    )

    if quantity < 1:
        return None

    risk_amount = (
        quantity
        * risk_per_share
    )

    if risk_amount > MAX_RISK_PER_TRADE:

        quantity = math.floor(
            MAX_RISK_PER_TRADE
            / risk_per_share
        )

        if quantity < 1:
            return None

        risk_amount = (
            quantity
            * risk_per_share
        )

    target = (
        entry
        + (
            risk_per_share
            * MIN_RR
        )
    )

    return {
        "entry_price": round(
            entry,
            2,
        ),

        "stop_loss": round(
            candle_low,
            2,
        ),

        "target_price": round(
            target,
            2,
        ),

        "quantity": int(
            quantity
        ),

        "risk_per_share": round(
            risk_per_share,
            4,
        ),

        "risk_amount": round(
            risk_amount,
            2,
        ),

        "risk_reward_ratio": MIN_RR,
    }


# ============================================================================
# STRATEGY VALIDATION
# ============================================================================

def run_strategy_validation(
    strategy: StrategyAnalysisSuite,
    snapshot: Dict[str, Any],
    trade_params: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Run the real StrategyAnalysisSuite.
    """

    context = {
        "ticker": snapshot[
            "canonical_symbol"
        ],

        "strategy_name": "EMA_PULLBACK",

        "close_price": snapshot[
            "close"
        ],

        "ema20": snapshot[
            "ema20"
        ],

        "ema50": snapshot[
            "ema50"
        ],

        "vwap": snapshot[
            "vwap"
        ],

        "rsi": snapshot[
            "rsi"
        ],

        "risk_reward_ratio":
            trade_params[
                "risk_reward_ratio"
            ],
    }

    return strategy.execute(
        context
    )


# ============================================================================
# SIGNAL
# ============================================================================

def build_shadow_signal(
    snapshot: Dict[str, Any],
    trade_params: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a standard BUY-only shadow signal.

    No broker payload is generated.
    """

    provider_symbol = snapshot[
        "provider_symbol"
    ]

    exchange = (
        "BSE"
        if provider_symbol.endswith(
            ".BO"
        )
        else "NSE"
    )

    return {
        "trading_symbol":
            snapshot[
                "canonical_symbol"
            ],

        "action": "BUY",

        "quantity":
            trade_params[
                "quantity"
            ],

        "trigger_price":
            snapshot[
                "close"
            ],

        "product_type": "CASH",

        "exchange": exchange,

        "risk_amount":
            trade_params[
                "risk_amount"
            ],

        "risk_reward_ratio":
            trade_params[
                "risk_reward_ratio"
            ],

        "entry_price":
            trade_params[
                "entry_price"
            ],

        "stop_loss":
            trade_params[
                "stop_loss"
            ],

        "target_price":
            trade_params[
                "target_price"
            ],

        "system_mode":
            SYSTEM_MODE,
    }


# ============================================================================
# RUNNER
# ============================================================================

class ShadowDailyRunner:

    def __init__(self):

        # Provider mapping.
        self.adapter = (
            ProviderSymbolAdapter()
        )

        # Frozen market-data validation.
        self.market_adapter = (
            MarketDataAdapter(
                max_stale_seconds=60
            )
        )

        # Actual strategy validator.
        self.strategy = (
            StrategyAnalysisSuite()
        )

        # Explicitly shadow-only session.
        self.broker = (
            ShadowOnlyBrokerSession()
        )

        # Frozen Phase 12 readiness auditor.
        self.auditor = (
            LiveReadinessAuditor(
                broker_session=self.broker,
                max_risk_per_trade_pct=1.0,
                max_trades_per_day=MAX_TRADES_PER_DAY,
            )
        )

        # Frozen Phase 12 failure harness.
        self.stress_harness = (
            FailureStressHarness(
                max_allowed_slippage_pct=
                    MAX_SLIPPAGE_PCT
            )
        )

        # Frozen Phase 12 shadow engine.
        self.shadow_engine = (
            ShadowExecutionEngine(
                readiness_auditor=
                    self.auditor,
                stress_harness=
                    self.stress_harness,
            )
        )

        # Frozen Phase 12 master orchestrator.
        self.phase12 = (
            Phase12MasterOrchestrator(
                broker_session=self.broker,
                auditor=self.auditor,
                stress_harness=self.stress_harness,
                shadow_engine=self.shadow_engine,
            )
        )

        # HARD SAFETY BOUNDARY.
        self.phase12.system_mode = "SHADOW"

        self.stats = {
            "universe_total": 0,
            "scanned": 0,
            "data_received": 0,
            "strategy_valid": 0,
            "governance_passed": 0,
            "risk_passed": 0,
            "shadow_executed": 0,
            "rejected": 0,
            "errors": 0,
            "provider_unresolved": 0,
            "provider_unavailable": 0,
        }

        self.results = []

    # ========================================================================

    def run(self):

        start_time = time.time()

        logger.info(
            "Initializing Shadow Daily Runner "
            "for canonical universe..."
        )

        symbols = (
            load_canonical_universe()
        )

        self.stats[
            "universe_total"
        ] = len(symbols)

        logger.info(
            "Account Equity : ₹%.2f",
            ACCOUNT_EQUITY,
        )

        logger.info(
            "Max Risk/Trade : ₹%.2f",
            MAX_RISK_PER_TRADE,
        )

        logger.info(
            "Max Trades/Day : %s",
            MAX_TRADES_PER_DAY,
        )

        logger.info(
            "Max Slippage   : %.2f%%",
            MAX_SLIPPAGE_PCT,
        )

        logger.info(
            "Minimum R:R    : %.2f",
            MIN_RR,
        )

        logger.info(
            "System Mode    : %s",
            self.phase12.system_mode,
        )

        for index, canonical_symbol in enumerate(
            symbols,
            start=1,
        ):

            logger.info(
                "[%s/%s] Processing %s",
                index,
                len(symbols),
                canonical_symbol,
            )

            self.stats[
                "scanned"
            ] += 1

            result = (
                self.process_symbol(
                    canonical_symbol
                )
            )

            self.results.append(
                result
            )

        summary = (
            self.build_summary(
                start_time
            )
        )

        self.write_results(
            summary
        )

        self.print_summary(
            summary
        )

        return summary

    # ========================================================================

    def process_symbol(
        self,
        canonical_symbol: str,
    ) -> Dict[str, Any]:

        result = {
            "timestamp_utc":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "canonical_symbol":
                canonical_symbol,

            "provider_symbol":
                None,

            "classification":
                None,

            "data_received":
                False,

            "strategy_valid":
                False,

            "risk_valid":
                False,

            "shadow_executed":
                False,

            "market": {},
            "strategy": {},
            "risk": {},
            "phase12": {},

            "error":
                None,
        }

        # ====================================================================
        # PROVIDER SYMBOL MAPPING
        # ====================================================================

        try:

            mapping = (
                self.adapter.resolve(
                    canonical_symbol
                )
            )

            provider_symbol = (
                mapping.get(
                    "provider_symbol"
                )
            )

            classification = (
                mapping.get(
                    "classification"
                )
            )

            result[
                "provider_symbol"
            ] = provider_symbol

            result[
                "classification"
            ] = classification

            if not provider_symbol:

                self.stats[
                    "provider_unresolved"
                ] += 1

                self.stats[
                    "rejected"
                ] += 1

                result[
                    "error"
                ] = (
                    "PROVIDER_SYMBOL_UNRESOLVED"
                )

                return result

        except Exception as exc:

            self.stats[
                "errors"
            ] += 1

            self.stats[
                "rejected"
            ] += 1

            result[
                "error"
            ] = (
                f"SYMBOL_ADAPTER_ERROR: {exc}"
            )

            return result

        # ====================================================================
        # MARKET DATA
        # ====================================================================

        df, provider_error = (
            fetch_market_data(
                provider_symbol
            )
        )

        if provider_error:

            self.stats[
                "provider_unavailable"
            ] += 1

            self.stats[
                "rejected"
            ] += 1

            result[
                "error"
            ] = provider_error

            return result

        # ====================================================================
        # MARKET SNAPSHOT / INDICATORS
        # ====================================================================

        try:

            snapshot = (
                get_latest_snapshot(
                    canonical_symbol,
                    provider_symbol,
                    df,
                )
            )

            result[
                "data_received"
            ] = True

            result[
                "market"
            ] = snapshot

            self.stats[
                "data_received"
            ] += 1

        except Exception as exc:

            self.stats[
                "errors"
            ] += 1

            self.stats[
                "rejected"
            ] += 1

            result[
                "error"
            ] = (
                "MARKET_DATA_VALIDATION_ERROR: "
                f"{exc}"
            )

            return result

        # ====================================================================
        # FROZEN MARKET DATA ADAPTER
        # ====================================================================

        normalized = (
            self.market_adapter
            .normalize_candle(
                {
                    "ticker":
                        canonical_symbol,

                    "open":
                        snapshot["open"],

                    "high":
                        snapshot["high"],

                    "low":
                        snapshot["low"],

                    "close":
                        snapshot["close"],

                    "volume":
                        snapshot["volume"],

                    "vwap":
                        snapshot["vwap"],

                    "timestamp":
                        snapshot["timestamp"],
                }
            )
        )

        if not normalized.get(
            "is_valid"
        ):

            self.stats[
                "rejected"
            ] += 1

            result[
                "error"
            ] = (
                "MARKET_DATA_ADAPTER_REJECTED: "
                + str(
                    normalized.get(
                        "error"
                    )
                )
            )

            return result

        # ====================================================================
        # SHADOW RISK PAYLOAD
        # ====================================================================

        trade_params = (
            build_shadow_trade_parameters(
                snapshot
            )
        )

        if trade_params is None:

            self.stats[
                "rejected"
            ] += 1

            result[
                "error"
            ] = (
                "NO_VALID_SHADOW_RISK_PARAMETERS"
            )

            return result

        result[
            "risk"
        ] = trade_params

        # ====================================================================
        # ACTUAL STRATEGY VALIDATION
        # ====================================================================

        try:

            strategy_result = (
                run_strategy_validation(
                    self.strategy,
                    snapshot,
                    trade_params,
                )
            )

            result[
                "strategy"
            ] = strategy_result

            if not strategy_result.get(
                "valid_setup",
                False,
            ):

                self.stats[
                    "rejected"
                ] += 1

                result[
                    "error"
                ] = (
                    "INVALID_STRATEGY_SETUP"
                )

                return result

            self.stats[
                "strategy_valid"
            ] += 1

            # Strategy validation is the technical gate.
            self.stats[
                "governance_passed"
            ] += 1

        except Exception as exc:

            self.stats[
                "errors"
            ] += 1

            self.stats[
                "rejected"
            ] += 1

            result[
                "error"
            ] = (
                "STRATEGY_VALIDATION_ERROR: "
                f"{exc}"
            )

            return result

        # ====================================================================
        # BUILD SHADOW SIGNAL
        # ====================================================================

        signal = (
            build_shadow_signal(
                snapshot,
                trade_params,
            )
        )

        result[
            "signal"
        ] = signal

        # ====================================================================
        # FROZEN PHASE 12 RISK INVARIANTS
        # ====================================================================

        total_equity = (
            ACCOUNT_EQUITY
        )

        trades_today = (
            self.stats[
                "shadow_executed"
            ]
        )

        risk_audit = (
            self.auditor
            .verify_risk_invariants(
                signal,
                total_equity,
                trades_today,
            )
        )

        result[
            "risk_audit"
        ] = risk_audit

        if not risk_audit.get(
            "passed"
        ):

            self.stats[
                "rejected"
            ] += 1

            result[
                "error"
            ] = (
                "RISK_INVARIANT_REJECTED: "
                + str(
                    risk_audit.get(
                        "reason"
                    )
                )
            )

            return result

        result[
            "risk_valid"
        ] = True

        self.stats[
            "risk_passed"
        ] += 1

        # ====================================================================
        # GLOBAL SHADOW TRADE LIMIT
        # ====================================================================

        if (
            self.stats[
                "shadow_executed"
            ]
            >= MAX_TRADES_PER_DAY
        ):

            self.stats[
                "rejected"
            ] += 1

            result[
                "error"
            ] = (
                "DAILY_SHADOW_TRADE_LIMIT_REACHED"
            )

            return result

        # ====================================================================
        # PHASE 12 ACCOUNT STATE
        # ====================================================================

        account_state = {
            "available_cash":
                ACCOUNT_EQUITY,

            "invested_value":
                0.0,

            "trades_today_count":
                self.stats[
                    "shadow_executed"
                ],

            "open_positions": [],

            "open_orders": [],
        }

        # ====================================================================
        # PHASE 12 SHADOW EXECUTION
        # ====================================================================

        try:

            phase12_result = (
                self.phase12
                .process_incoming_signal(
                    signal=signal,
                    market_price=
                        snapshot["close"],
                    account_state=
                        account_state,
                )
            )

            result[
                "phase12"
            ] = phase12_result

            status = (
                phase12_result.get(
                    "status"
                )
            )

            if status == (
                "FILLED_SHADOW"
            ):

                self.stats[
                    "shadow_executed"
                ] += 1

                result[
                    "shadow_executed"
                ] = True

            else:

                self.stats[
                    "rejected"
                ] += 1

        except Exception as exc:

            self.stats[
                "errors"
            ] += 1

            self.stats[
                "rejected"
            ] += 1

            result[
                "error"
            ] = (
                "PHASE12_ERROR: "
                f"{exc}"
            )

        return result

    # ========================================================================

    def build_summary(
        self,
        start_time: float,
    ) -> Dict[str, Any]:

        telemetry = (
            self.shadow_engine
            .get_telemetry_summary()
        )

        elapsed = round(
            time.time()
            - start_time,
            3,
        )

        return {
            "timestamp_utc":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "system":
                "Halal Trading OS",

            "mode":
                "SHADOW",

            "universe_file":
                str(
                    CANONICAL_UNIVERSE
                ),

            "universe_count":
                self.stats[
                    "universe_total"
                ],

            "account_equity":
                ACCOUNT_EQUITY,

            "max_risk_per_trade":
                MAX_RISK_PER_TRADE,

            "max_trades_per_day":
                MAX_TRADES_PER_DAY,

            "max_slippage_pct":
                MAX_SLIPPAGE_PCT,

            "min_rr_ratio":
                MIN_RR,

            "statistics":
                self.stats,

            "phase12_telemetry":
                telemetry,

            "elapsed_seconds":
                elapsed,

            "live_orders_submitted":
                0,

            "live_execution_enabled":
                False,

            "kill_switch_active":
                self.phase12
                .kill_switch_active,

            "system_status":
                (
                    "SHADOW_COMPLETE"
                    if self.stats[
                        "errors"
                    ] == 0
                    else
                    "SHADOW_COMPLETE_WITH_ERRORS"
                ),
        }

    # ========================================================================

    def write_results(
        self,
        summary: Dict[str, Any],
    ):

        date_stamp = (
            datetime.now()
            .strftime("%Y%m%d")
        )

        results_file = (
            LOG_DIR
            / (
                "shadow_daily_results_"
                f"{date_stamp}.json"
            )
        )

        summary_file = (
            AUDIT_DIR
            / (
                "shadow_daily_audit_"
                f"{date_stamp}.json"
            )
        )

        payload = {
            "summary":
                summary,

            "results":
                self.results,
        }

        with open(
            results_file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                payload,
                f,
                indent=2,
                ensure_ascii=False,
            )

        with open(
            summary_file,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                summary,
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(
            "Detailed results saved: %s",
            results_file,
        )

        logger.info(
            "Daily audit saved: %s",
            summary_file,
        )

    # ========================================================================

    @staticmethod
    def print_summary(
        summary: Dict[str, Any],
    ):

        stats = summary[
            "statistics"
        ]

        print()
        print("=" * 72)
        print(
            "HALAL TRADING OS — "
            "SHADOW DAILY RUN SUMMARY"
        )
        print("=" * 72)

        print(
            f"Universe Total      : "
            f"{stats['universe_total']}"
        )

        print(
            f"Scanned             : "
            f"{stats['scanned']}"
        )

        print(
            f"Data Received       : "
            f"{stats['data_received']}"
        )

        print(
            f"Strategy Valid      : "
            f"{stats['strategy_valid']}"
        )

        print(
            f"Governance Passed   : "
            f"{stats['governance_passed']}"
        )

        print(
            f"Risk Passed         : "
            f"{stats['risk_passed']}"
        )

        print(
            f"Shadow Executed     : "
            f"{stats['shadow_executed']}"
        )

        print(
            f"Rejected            : "
            f"{stats['rejected']}"
        )

        print(
            f"Errors              : "
            f"{stats['errors']}"
        )

        print(
            f"Provider Unresolved : "
            f"{stats['provider_unresolved']}"
        )

        print(
            f"Provider Unavailable: "
            f"{stats['provider_unavailable']}"
        )

        print()

        print(
            f"Account Equity      : "
            f"₹{ACCOUNT_EQUITY:,.2f}"
        )

        print(
            f"Max Risk / Trade    : "
            f"₹{MAX_RISK_PER_TRADE:,.2f}"
        )

        print(
            f"Max Trades / Day    : "
            f"{MAX_TRADES_PER_DAY}"
        )

        print(
            f"System Mode         : "
            f"{summary['mode']}"
        )

        print(
            f"Live Orders         : "
            f"{summary['live_orders_submitted']}"
        )

        print(
            f"Live Execution      : "
            f"{summary['live_execution_enabled']}"
        )

        print(
            f"Kill Switch Active  : "
            f"{summary['kill_switch_active']}"
        )

        print(
            f"Runtime             : "
            f"{summary['elapsed_seconds']} sec"
        )

        print("=" * 72)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":

    try:

        runner = (
            ShadowDailyRunner()
        )

        runner.run()

    except KeyboardInterrupt:

        logger.warning(
            "Shadow Daily Runner interrupted by operator."
        )

        sys.exit(130)

    except Exception as exc:

        logger.exception(
            "FATAL SHADOW RUNNER ERROR: %s",
            exc,
        )

        sys.exit(1)