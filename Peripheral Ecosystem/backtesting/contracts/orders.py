"""
Order and Execution Contracts.
Defines simulated orders, fills, and position states.
"""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SimulatedOrder:
    order_id: str
    symbol: str
    direction: str
    order_type: str
    quantity: float
    limit_price: float = 0.0
    stop_price: float = 0.0
