import uuid
from capacity_planning.contracts.capacity_contract import CapacityForecast

class CapacityForecaster:
    """
    Analyzes historical growth trends to forecast future workload capacity
    and determine associated capacity risk states.
    """
    def forecast_capacity(self, component: str, current_value: float, growth_rate: float, horizon_days: int = 30) -> CapacityForecast:
        projected = current_value * ((1.0 + growth_rate) ** (horizon_days / 30.0))
        projected = round(projected, 2)

        ratio = projected / (current_value if current_value > 0 else 1.0)
        risk_state = "NORMAL"
        if ratio > 2.0:
            risk_state = "CAPACITY_CRITICAL"
        elif ratio > 1.5:
            risk_state = "CAPACITY_RISK"
        elif ratio > 1.2:
            risk_state = "WATCH"

        return CapacityForecast(
            forecast_id=str(uuid.uuid4())[:8],
            target_component=component,
            current_workload_metric=current_value,
            projected_workload_metric=projected,
            time_horizon_days=horizon_days,
            risk_state=risk_state,
            confidence_score=0.82
        )
