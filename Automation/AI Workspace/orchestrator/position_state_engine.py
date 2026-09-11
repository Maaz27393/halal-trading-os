from typing import Dict, Any, Optional

class Position:
    """Represents an active long equity position."""
    def __init__(self, ticker: str, qty: int, entry_price: float, stop_loss: float, target_price: float):
        self.ticker = ticker.upper()
        self.qty = qty
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.target_price = target_price
        self.current_price = entry_price

    @property
    def invested_capital(self) -> float:
        return round(self.qty * self.entry_price, 2)

    @property
    def current_value(self) -> float:
        return round(self.qty * self.current_price, 2)

    @property
    def unrealized_pnl(self) -> float:
        return round(self.current_value - self.invested_capital, 2)

    @property
    def unrealized_pnl_pct(self) -> float:
        if self.invested_capital == 0:
            return 0.0
        return round((self.unrealized_pnl / self.invested_capital) * 100.0, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticker": self.ticker,
            "qty": self.qty,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "target_price": self.target_price,
            "current_price": self.current_price,
            "invested_capital": self.invested_capital,
            "current_value": self.current_value,
            "unrealized_pnl": self.unrealized_pnl,
            "unrealized_pnl_pct": self.unrealized_pnl_pct
        }

class PositionStateEngine:
    """
    Phase 9B: Position State Engine
    Tracks cash reserves, active open positions, mark-to-market adjustments,
    and handles position liquidation & realized PnL calculations.
    """
    def __init__(self, initial_capital: float = 100000.0):
        self.total_capital = initial_capital
        self.available_capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.closed_positions_pnl: float = 0.0

    def open_position(self, ticker: str, qty: int, entry_price: float, stop_loss: float, target_price: float) -> Dict[str, Any]:
        ticker = ticker.upper()
        if ticker in self.positions:
            return {"success": False, "reason": f"Position already open for {ticker}"}

        cost = qty * entry_price
        if cost > self.available_capital:
            return {"success": False, "reason": f"Insufficient capital: required {cost:.2f}, available {self.available_capital:.2f}"}

        # Long position parameter validation
        if stop_loss >= entry_price or target_price <= entry_price:
            return {"success": False, "reason": "Invalid Risk/Reward boundary: Stop Loss must be < Entry and Target > Entry"}

        pos = Position(ticker, qty, entry_price, stop_loss, target_price)
        self.positions[ticker] = pos
        self.available_capital -= cost

        return {"success": True, "position": pos.to_dict()}

    def update_market_price(self, ticker: str, current_price: float):
        ticker = ticker.upper()
        if ticker in self.positions:
            self.positions[ticker].current_price = current_price

    def close_position(self, ticker: str, exit_price: float) -> Dict[str, Any]:
        ticker = ticker.upper()
        if ticker not in self.positions:
            return {"success": False, "reason": f"No active position for {ticker}"}

        pos = self.positions.pop(ticker)
        proceeds = pos.qty * exit_price
        pnl = proceeds - pos.invested_capital

        self.available_capital += proceeds
        self.closed_positions_pnl += pnl

        return {
            "success": True,
            "ticker": ticker,
            "entry_price": pos.entry_price,
            "exit_price": exit_price,
            "realized_pnl": round(pnl, 2),
            "available_capital": round(self.available_capital, 2)
        }

    def get_summary(self) -> Dict[str, Any]:
        unrealized = sum(p.unrealized_pnl for p in self.positions.values())
        allocated = sum(p.invested_capital for p in self.positions.values())
        portfolio_value = self.available_capital + allocated + unrealized
        return {
            "total_portfolio_value": round(portfolio_value, 2),
            "available_capital": round(self.available_capital, 2),
            "allocated_capital": round(allocated, 2),
            "active_positions_count": len(self.positions),
            "unrealized_pnl": round(unrealized, 2),
            "realized_pnl": round(self.closed_positions_pnl, 2)
        }
