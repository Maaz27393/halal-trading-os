from dataclasses import dataclass
from typing import Tuple, Optional, Sequence, List, Any
import pandas as pd
import numpy as np
from src.execution_harness import TradeRecord

class ContractViolationError(Exception):
    """Raised when an input contract or valuation precondition is violated."""
    pass

class InsufficientCapitalError(Exception):
    """Raised when allocated capital exceeds available cash."""
    pass

@dataclass(frozen=True)
class AllocationContract:
    sizing_mode: str
    allocation_value: float

@dataclass(frozen=True)
class ValuationBar:
    timestamp: pd.Timestamp
    close: float

@dataclass(frozen=True)
class PerformanceInput:
    initial_capital: float
    trades: Tuple[TradeRecord, ...]
    allocation_contract: Optional[AllocationContract]
    bars: Tuple[ValuationBar, ...]
    risk_free_rate_annual: float = 0.0
    periods_per_year: int = 252

@dataclass(frozen=True)
class EquityPoint:
    timestamp: pd.Timestamp
    total_equity: float
    cash: float
    position_value: float
    valuation_state: str

@dataclass(frozen=True)
class ReturnPoint:
    timestamp: pd.Timestamp
    return_val: float

@dataclass(frozen=True)
class DrawdownPoint:
    timestamp: pd.Timestamp
    drawdown: float
    duration_bars: int

@dataclass(frozen=True)
class PerformanceMetrics:
    sharpe_ratio: Optional[float]
    sortino_ratio: Optional[float]
    cagr: Optional[float]
    annualized_volatility: float
    max_drawdown_duration_bars: int

@dataclass(frozen=True)
class PerformanceResult:
    equity_curve: Tuple[EquityPoint, ...]
    return_series: Tuple[ReturnPoint, ...]
    drawdown_series: Tuple[DrawdownPoint, ...]
    metrics: PerformanceMetrics
    terminal_state: str

class PerformanceEngine:
    def __init__(self, input_data: PerformanceInput):
        # 1. Validate preconditions and contracts
        if input_data.initial_capital <= 0:
            raise ContractViolationError("Initial capital must be strictly positive.")
        if not input_data.bars:
            raise ContractViolationError("Bars tuple cannot be empty.")

        
        previous_timestamp: Optional[pd.Timestamp] = None

        for bar in input_data.bars:
            timestamp = bar.timestamp

            # v1.3: timestamps must be explicitly UTC and timezone-aware.
            if timestamp.tzinfo is None or str(timestamp.tz) != "UTC":
                raise ContractViolationError(
                    f"ValuationBar timestamp must be explicitly UTC: {timestamp}"
                )

            # v1.3: timestamps must be strictly increasing and unique.
            if previous_timestamp is not None and timestamp <= previous_timestamp:
                raise ContractViolationError(
                    "ValuationBar timestamps must be strictly increasing and unique."
                )

            # v1.3: close must be finite and strictly positive.
            if not np.isfinite(bar.close) or bar.close <= 0:
                raise ContractViolationError(
                    f"ValuationBar close must be finite and strictly positive: {bar.close}"
                )

            previous_timestamp = timestamp

        self.input = input_data

    def run(self) -> PerformanceResult:
        if self.input.allocation_contract is None:
            raise ContractViolationError("Allocation contract is missing.")
        contract = self.input.allocation_contract
        initial_capital = self.input.initial_capital
        bars = self.input.bars
        trades = self.input.trades

        if contract.sizing_mode != "FIXED_CAPITAL":
            raise ContractViolationError(f"Unsupported sizing mode: {contract.sizing_mode}")
        
        alloc_val = contract.allocation_value

        # v1.3: FIXED_CAPITAL allocation must be finite and strictly positive.
        if not np.isfinite(alloc_val) or alloc_val <= 0:
            raise ContractViolationError(
                "FIXED_CAPITAL allocation value must be finite and strictly positive."
            )

        if alloc_val > initial_capital:
            raise InsufficientCapitalError(f"Allocation value {alloc_val} exceeds initial capital {initial_capital}")

        cash = initial_capital
        equity_curve: List[EquityPoint] = []
        
        # Map trades by entry time and exit time for lookup
        # Each trade uses certified entry_price and exit_price
        active_trades = list(trades)
        current_position: Optional[Tuple[TradeRecord, float]] = None # (trade, quantity)

        # Input ordering has already been contract-validated.
        # Do not reorder invalid input silently.
        for bar in bars:
            # Check for trade entries at or before this bar timestamp
            # If no active position, check if any trade starts on or before this bar
            if current_position is None and active_trades:
                # Find trade whose entry matches or precedes current bar
                matching_trade = None
                for t in active_trades:
                    if t.entry_timestamp <= bar.timestamp:
                        matching_trade = t
                        break
                if matching_trade:
                    active_trades.remove(matching_trade)
                    if alloc_val > cash:
                        raise InsufficientCapitalError("Insufficient cash during trade entry allocation.")
                    cash -= alloc_val
                    # Certified entry price sizing
                    quantity = alloc_val / matching_trade.entry_price
                    current_position = (matching_trade, quantity)

            # Mark-to-market valuation
            position_value = 0.0
            valuation_state = "FLAT"

            if current_position is not None:
                trade, qty = current_position
                # Check if trade exits at or before this bar timestamp
                if trade.exit_timestamp <= bar.timestamp:
                    # Trade exited: realize PnL using certified exit_price
                    proceeds = qty * trade.exit_price
                    cash += proceeds
                    current_position = None
                    position_value = 0.0
                    valuation_state = "FLAT"
                else:
                    # Active holding bar: value using explicit bar.close
                    position_value = qty * bar.close
                    valuation_state = "ACTIVE"

            total_equity = cash + position_value
            equity_curve.append(EquityPoint(
                timestamp=bar.timestamp,
                total_equity=total_equity,
                cash=cash,
                position_value=position_value,
                valuation_state=valuation_state
            ))

        # Compute return series
        return_series: List[ReturnPoint] = []
        for i in range(1, len(equity_curve)):
            e_prev = equity_curve[i-1].total_equity
            e_curr = equity_curve[i].total_equity
            ret = (e_curr / e_prev) - 1.0 if e_prev > 0 else 0.0
            return_series.append(ReturnPoint(
                timestamp=equity_curve[i].timestamp,
                return_val=ret
            ))

        # Compute drawdown series and max drawdown duration bars
        drawdown_series: List[DrawdownPoint] = []
        peak = equity_curve[0].total_equity
        max_dd_duration = 0
        current_dd_duration = 0

        for pt in equity_curve:
            if pt.total_equity > peak:
                peak = pt.total_equity
                current_dd_duration = 0
            elif pt.total_equity < peak:
                current_dd_duration += 1
            
            dd = (pt.total_equity / peak) - 1.0 if peak > 0 else 0.0
            if dd < 0:
                if current_dd_duration > max_dd_duration:
                    max_dd_duration = current_dd_duration
            else:
                current_dd_duration = 0

            drawdown_series.append(DrawdownPoint(
                timestamp=pt.timestamp,
                drawdown=dd,
                duration_bars=current_dd_duration
            ))

        # Compute metrics
        returns_arr = np.array([r.return_val for r in return_series]) if return_series else np.array([])
        periods = self.input.periods_per_year
        rf_annual = self.input.risk_free_rate_annual
        rf_period = rf_annual / periods

        sharpe_ratio: Optional[float] = None
        sortino_ratio: Optional[float] = None
        cagr: Optional[float] = None
        annualized_vol = 0.0

        if len(returns_arr) >= 2:
            mean_ret = np.mean(returns_arr)
            sigma = np.std(returns_arr, ddof=1)
            annualized_vol = sigma * np.sqrt(periods)
            if sigma > 1e-12:
                sharpe_ratio = ((mean_ret - rf_period) / sigma) * np.sqrt(periods)
            else:
                sharpe_ratio = 0.0

            # Sortino ratio calculation
            # v1.3: downside deviation uses total valid observations n as denominator,
            # while only returns below the target contribute to the numerator sum.
            downside_mask = returns_arr < rf_period
            if np.any(downside_mask):
                squared_downside_diffs = np.sum(
                    (returns_arr[downside_mask] - rf_period) ** 2
                )
                downside_std = np.sqrt(
                    squared_downside_diffs / len(returns_arr)
                )
                if downside_std > 1e-12:
                    sortino_ratio = ((mean_ret - rf_period) / downside_std) * np.sqrt(periods)
                else:
                    sortino_ratio = None
            else:
                sortino_ratio = None

        # CAGR calculation
        if len(equity_curve) >= 2 and equity_curve[0].total_equity > 0 and equity_curve[-1].total_equity > 0:
            e0 = equity_curve[0].total_equity
            e_t = equity_curve[-1].total_equity
            t_periods = len(equity_curve) - 1
            if t_periods > 0:
                cagr = (e_t / e0) ** (periods / t_periods) - 1.0

        metrics = PerformanceMetrics(
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            cagr=cagr,
            annualized_volatility=annualized_vol,
            max_drawdown_duration_bars=max_dd_duration
        )

        return PerformanceResult(
            equity_curve=tuple(equity_curve),
            return_series=tuple(return_series),
            drawdown_series=tuple(drawdown_series),
            metrics=metrics,
            terminal_state="NORMAL"
        )




