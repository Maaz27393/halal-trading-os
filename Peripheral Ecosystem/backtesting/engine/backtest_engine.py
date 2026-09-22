import logging
from typing import List
from backtesting.contracts.backtest_contract import OHLCVBar, TradeSignal, TradeResult, BacktestReport

logger = logging.getLogger("BacktestEngine")

class BacktestEngine:
    """
    Purely analytical backtesting engine. Strictly non-execution (LIVE_AUTO_EXECUTION = FALSE).
    """
    def __init__(self, initial_capital: float = 100000.0, slippage_pct: float = 0.05, brokerage_fee: float = 20.0):
        self.initial_capital = initial_capital
        self.slippage_pct = slippage_pct
        self.brokerage_fee = brokerage_fee
        self.live_auto_execution = False
        logger.info("BacktestEngine initialized in read-only / simulation mode (LIVE_AUTO_EXECUTION = FALSE).")

    def run_simulation(self, strategy_name: str, symbol: str, bars: List[OHLCVBar], signal: TradeSignal) -> BacktestReport:
        """Simulates a trade against historical OHLCV bars incorporating slippage and costs."""
        if self.live_auto_execution:
            raise RuntimeError("CRITICAL: Backtest engine attempted live execution! Halting immediately.")

        logger.info(f"Running backtest simulation for {symbol} using strategy '{strategy_name}'...")
        
        trades: List[TradeResult] = []
        position_open = False
        entry_price = signal.entry_price * (1.0 + (self.slippage_pct / 100.0) if signal.direction == "LONG" else 1.0 - (self.slippage_pct / 100.0))
        entry_time = signal.entry_time

        exit_price = entry_price
        exit_time = entry_time
        outcome = "EXPIRED"
        pnl = 0.0

        for bar in bars:
            if bar.timestamp < signal.entry_time:
                continue
            
            if signal.direction == "LONG":
                if bar.low <= signal.stop_loss:
                    exit_price = signal.stop_loss
                    exit_time = bar.timestamp
                    outcome = "STOP_LOSS_HIT"
                    pnl = (exit_price - entry_price) - self.brokerage_fee
                    position_open = True
                    break
                elif bar.high >= signal.target_price:
                    exit_price = signal.target_price
                    exit_time = bar.timestamp
                    outcome = "TARGET_HIT"
                    pnl = (exit_price - entry_price) - self.brokerage_fee
                    position_open = True
                    break

        if not position_open and bars:
            # Close at final bar if neither SL nor target hit
            final_bar = bars[-1]
            exit_price = final_bar.close
            exit_time = final_bar.timestamp
            outcome = "EXPIRED"
            pnl = (exit_price - entry_price) - self.brokerage_fee

        pnl_pct = (pnl / entry_price) * 100.0
        trade_result = TradeResult(
            symbol=symbol,
            entry_time=entry_time,
            exit_time=exit_time,
            entry_price=entry_price,
            exit_price=exit_price,
            direction=signal.direction,
            pnl=round(pnl, 2),
            pnl_percentage=round(pnl_pct, 2),
            outcome=outcome
        )
        trades.append(trade_result)

        winning = 1 if pnl > 0 else 0
        losing = 0 if pnl > 0 else 1

        return BacktestReport(
            strategy_name=strategy_name,
            total_trades=1,
            winning_trades=winning,
            losing_trades=losing,
            win_rate=100.0 if winning == 1 else 0.0,
            net_pnl=round(pnl, 2),
            max_drawdown=round(abs(pnl_pct) if pnl < 0 else 0.0, 2),
            trades=trades
        )
