from typing import Dict, Any, Optional

class Position:
    def __init__(self, ticker: str, qty: int, entry_price: float, stop_loss: float, target_price: float):
        self.ticker = ticker
        self.qty = qty
        self.entry_price = entry_price
        self.current_price = entry_price
        self.stop_loss = stop_loss
        self.target_price = target_price
        self.unrealized_pnl = 0.0
        self.current_value = qty * entry_price

    def update_price(self, price: float):
        self.current_price = price
        self.current_value = self.qty * price
        self.unrealized_pnl = round((price - self.entry_price) * self.qty, 2)

class PositionStateEngine:
    """
    Phase 9B: Position State Engine
    Tracks live position holdings, capital allocation, stop-loss/target bounds,
    and portfolio mark-to-market valuations.
    """
    def __init__(self, initial_capital: float = 200000.0):
        self.initial_capital = initial_capital
        self.available_capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.realized_pnl = 0.0

    def open_position(self, ticker: str, qty: int, entry_price: float, stop_loss: float, target_price: float) -> Dict[str, Any]:
        cost = qty * entry_price
        if cost > self.available_capital:
            return {"success": False, "reason": f"Insufficient capital: required {cost}, available {self.available_capital}"}
        
        if ticker in self.positions:
            pos = self.positions[ticker]
            total_qty = pos.qty + qty
            pos.entry_price = round(((pos.qty * pos.entry_price) + cost) / total_qty, 2)
            pos.qty = total_qty
            pos.update_price(entry_price)
        else:
            self.positions[ticker] = Position(ticker, qty, entry_price, stop_loss, target_price)

        self.available_capital -= cost
        return {"success": True, "position": self.positions[ticker]}

    def close_position(self, ticker: str, exit_price: float) -> Dict[str, Any]:
        if ticker not in self.positions:
            return {"success": False, "reason": f"No open position found for {ticker}"}

        pos = self.positions.pop(ticker)
        proceeds = pos.qty * exit_price
        pnl = round((exit_price - pos.entry_price) * pos.qty, 2)
        self.available_capital += proceeds
        self.realized_pnl += pnl

        return {"success": True, "realized_pnl": pnl, "proceeds": proceeds}

    def update_market_price(self, ticker: str, price: float):
        if ticker in self.positions:
            self.positions[ticker].update_price(price)

    def get_portfolio_summary(self) -> Dict[str, Any]:
        total_unrealized = sum(p.unrealized_pnl for p in self.positions.values())
        total_position_val = sum(p.current_value for p in self.positions.values())
        return {
            "initial_capital": self.initial_capital,
            "available_capital": self.available_capital,
            "open_positions_count": len(self.positions),
            "total_unrealized_pnl": total_unrealized,
            "total_realized_pnl": self.realized_pnl,
            "total_equity": round(self.available_capital + total_position_val, 2)
        }
