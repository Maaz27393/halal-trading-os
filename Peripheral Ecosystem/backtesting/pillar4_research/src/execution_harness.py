from __future__ import annotations

import pandas as pd
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from src.backtest_dataset import BacktestDataset
from src.backtesting_engine import StrategyContract, BacktestingEngine

class ExecutionHarnessError(Exception):
    """Raised when execution simulation encounters invalid states."""
    pass

@dataclass(frozen=True)
class ExecutionConfig:
    slippage_pct: float = 0.0
    transaction_cost_pct: float = 0.0
    default_stop_loss_pct: Optional[float] = None
    default_target_pct: Optional[float] = None

@dataclass(frozen=True)
class TradeRecord:
    entry_timestamp: pd.Timestamp
    entry_price: float
    exit_timestamp: pd.Timestamp
    exit_price: float
    direction: str  # "LONG" or "SHORT"
    exit_reason: str  # "STOP", "TARGET", "STRATEGY_EXIT", "END_OF_DATA"
    pnl: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class ExecutionHarness:
    """
    Research-only execution simulation harness.
    Decoupled from strategies and completely devoid of live broker dependencies (R22).
    """
    def __init__(self, strategy: StrategyContract, config: Optional[ExecutionConfig] = None):
        self.strategy = strategy
        self.config = config or ExecutionConfig()
        self._engine = BacktestingEngine(strategy=self.strategy)

    def run(self, dataset: BacktestDataset) -> List[TradeRecord]:
        if not isinstance(dataset, BacktestDataset):
            raise TypeError("ExecutionHarness requires a verified BacktestDataset instance.")

        trades: List[TradeRecord] = []
        active_position: Optional[Dict[str, Any]] = None

        # Lifecycle initialization
        self.strategy.on_start(dataset)

        df = dataset.df._df if hasattr(dataset.df, '_df') else dataset.df
        total_rows = len(df)

        for idx, row in df.iterrows():
            bar_index = int(idx) if isinstance(idx, int) else 0
            timestamp = row.get("timestamp", pd.Timestamp.now(tz="UTC"))
            open_p = float(row.get("open", row.get("close", 0.0)))
            high_p = float(row.get("high", row.get("close", 0.0)))
            low_p = float(row.get("low", row.get("close", 0.0)))
            close_p = float(row.get("close", 0.0))

            # 1. If in an active position, check exit conditions (Stop, Target, Strategy Exit)
            if active_position is not None:
                direction = active_position["direction"]
                stop_loss = active_position["stop_loss"]
                target = active_position["target"]
                exit_triggered = False
                exit_price = 0.0
                exit_reason = ""

                if direction == "LONG":
                    hit_stop = low_p <= stop_loss
                    hit_target = high_p >= target

                    if hit_stop and hit_target:
                        # R21: Conservative same-bar collision policy -> Stop takes precedence
                        exit_triggered = True
                        exit_price = stop_loss
                        exit_reason = "STOP"
                    elif hit_stop:
                        exit_triggered = True
                        exit_price = stop_loss
                        exit_reason = "STOP"
                    elif hit_target:
                        exit_triggered = True
                        exit_price = target
                        exit_reason = "TARGET"

                if exit_triggered:
                    pnl = exit_price - active_position["entry_price"] if direction == "LONG" else active_position["entry_price"] - exit_price
                    trades.append(TradeRecord(
                        entry_timestamp=active_position["entry_timestamp"],
                        entry_price=active_position["entry_price"],
                        exit_timestamp=timestamp,
                        exit_price=exit_price,
                        direction=direction,
                        exit_reason=exit_reason,
                        pnl=pnl,
                        metadata=active_position.get("metadata", {})
                    ))
                    active_position = None

            # 2. Query strategy for signal / intent on current bar
            signal = self.strategy.on_bar(bar_index, row)
            if not isinstance(signal, dict):
                signal = {"action": "HOLD"}

            action = signal.get("action", "HOLD").upper()

            # 3. Handle entry intent if flat
            if active_position is None and action in ["BUY", "LONG"]:
                entry_price = close_p * (1.0 + self.config.slippage_pct)
                sl = signal.get("stop_loss", entry_price * (1.0 - (self.config.default_stop_loss_pct or 0.02)))
                tgt = signal.get("target", entry_price * (1.0 + (self.config.default_target_pct or 0.05)))

                active_position = {
                    "direction": "LONG",
                    "entry_timestamp": timestamp,
                    "entry_price": entry_price,
                    "stop_loss": sl,
                    "target": tgt,
                    "metadata": signal.get("metadata", {})
                }

            # If last bar and still in position, close at close price
            if bar_index == total_rows - 1 and active_position is not None:
                exit_price = close_p
                pnl = exit_price - active_position["entry_price"]
                trades.append(TradeRecord(
                    entry_timestamp=active_position["entry_timestamp"],
                    entry_price=active_position["entry_price"],
                    exit_timestamp=timestamp,
                    exit_price=exit_price,
                    direction=active_position["direction"],
                    exit_reason="END_OF_DATA",
                    pnl=pnl,
                    metadata=active_position.get("metadata", {})
                ))
                active_position = None

        # Lifecycle finalization
        self.strategy.on_finish()
        return trades
