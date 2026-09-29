from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.backtest_dataset import BacktestDataset
from src.backtesting_engine import StrategyContract
from src.execution_harness import ExecutionHarness, ExecutionConfig, TradeRecord

# Engine & Simulator Version Constants
ENGINE_VERSION = "P4.4-Engine-1.0.0"
SIMULATOR_VERSION = "P4.4-Simulator-1.0.0"

@dataclass(frozen=True)
class ExecutionConfigDTO:
    slippage_pct: float
    transaction_cost_pct: float
    default_stop_loss_pct: Optional[float]
    default_target_pct: Optional[float]

    @classmethod
    def from_config(cls, config: ExecutionConfig) -> ExecutionConfigDTO:
        return cls(
            slippage_pct=config.slippage_pct,
            transaction_cost_pct=config.transaction_cost_pct,
            default_stop_loss_pct=config.default_stop_loss_pct,
            default_target_pct=config.default_target_pct
        )

def compute_run_identity(
    dataset_identity: str,
    dataset_sha256: str,
    calendar_sha256: str,
    strategy_id: str,
    strategy_version: str,
    config: ExecutionConfigDTO,
    engine_version: str,
    simulator_version: str
) -> str:
    """Computes a deterministic cryptographic SHA256 run identity hash from provenance inputs."""
    payload = {
        "dataset_identity": dataset_identity,
        "dataset_sha256": dataset_sha256,
        "calendar_sha256": calendar_sha256,
        "strategy_id": strategy_id,
        "strategy_version": strategy_version,
        "execution_config": {
            "slippage_pct": config.slippage_pct,
            "transaction_cost_pct": config.transaction_cost_pct,
            "default_stop_loss_pct": config.default_stop_loss_pct,
            "default_target_pct": config.default_target_pct
        },
        "engine_version": engine_version,
        "simulator_version": simulator_version
    }
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

@dataclass(frozen=True)
class BacktestRunRecord:
    run_id: str
    dataset_identity: str
    dataset_sha256: str
    calendar_sha256: str
    strategy_id: str
    strategy_version: str
    execution_config: ExecutionConfigDTO
    engine_version: str
    simulator_version: str
    trade_records: List[TradeRecord] = field(default_factory=list)

class BacktestRunManager:
    """
    Manages execution runs and compiles immutable cryptographic run provenance records (R23, R24).
    """
    def __init__(self, strategy: StrategyContract, config: Optional[ExecutionConfig] = None):
        self.strategy = strategy
        self.config = config or ExecutionConfig()
        self.harness = ExecutionHarness(strategy=self.strategy, config=self.config)

    def execute_run(self, dataset: BacktestDataset) -> BacktestRunRecord:
        if not isinstance(dataset, BacktestDataset):
            raise TypeError("BacktestRunManager requires a verified BacktestDataset instance.")

        strategy_version = getattr(self.strategy, "version", "1.0.0")
        strategy_id = self.strategy.name

        config_dto = ExecutionConfigDTO.from_config(self.config)

        run_id = compute_run_identity(
            dataset_identity=dataset.dataset_identity,
            dataset_sha256=dataset.dataset_sha256,
            calendar_sha256=dataset.calendar_sha256,
            strategy_id=strategy_id,
            strategy_version=strategy_version,
            config=config_dto,
            engine_version=ENGINE_VERSION,
            simulator_version=SIMULATOR_VERSION
        )

        trades = self.harness.run(dataset)

        return BacktestRunRecord(
            run_id=run_id,
            dataset_identity=dataset.dataset_identity,
            dataset_sha256=dataset.dataset_sha256,
            calendar_sha256=dataset.calendar_sha256,
            strategy_id=strategy_id,
            strategy_version=strategy_version,
            execution_config=config_dto,
            engine_version=ENGINE_VERSION,
            simulator_version=SIMULATOR_VERSION,
            trade_records=trades
        )
