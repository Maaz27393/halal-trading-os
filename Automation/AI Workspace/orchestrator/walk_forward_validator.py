from typing import List, Dict, Any, Tuple

class WalkForwardValidator:
    """
    Phase 10E: Walk-Forward Validation Engine
    Splits chronological datasets into In-Sample (IS) and Out-Of-Sample (OOS) windows
    to verify strategy robustness, detect curve-fitting, and calculate Walk-Forward Efficiency (WFE).
    """
    def __init__(self, is_ratio: float = 0.70):
        self.is_ratio = is_ratio

    def split_chronological_feed(self, candle_feed: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Splits a single time-series feed into chronological In-Sample and Out-Of-Sample feeds."""
        if not candle_feed:
            return [], []
        
        split_idx = int(len(candle_feed) * self.is_ratio)
        is_feed = candle_feed[:split_idx]
        oos_feed = candle_feed[split_idx:]
        return is_feed, oos_feed

    def calculate_wfe(self, is_metrics: Dict[str, Any], oos_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates Walk-Forward Efficiency Ratio (WFE):
        WFE = (OOS Annualized/Per-Trade Return) / (IS Annualized/Per-Trade Return) * 100
        A WFE > 50-60% indicates robust non-overfitted performance across market regimes.
        """
        is_exp = is_metrics.get("expectancy_per_trade", 0.0)
        oos_exp = oos_metrics.get("expectancy_per_trade", 0.0)

        is_profit = is_metrics.get("net_profit", 0.0)
        oos_profit = oos_metrics.get("net_profit", 0.0)

        # Calculate WFE based on per-trade expectancy ratio
        if is_exp > 0:
            wfe_ratio_pct = round((oos_exp / is_exp) * 100.0, 2)
        elif is_exp == 0 and oos_exp == 0:
            wfe_ratio_pct = 0.0
        else:
            wfe_ratio_pct = -100.0 if oos_exp < 0 else 0.0

        is_robust = wfe_ratio_pct >= 50.0 and oos_profit > 0

        return {
            "is_net_profit": is_profit,
            "oos_net_profit": oos_profit,
            "is_expectancy": is_exp,
            "oos_expectancy": oos_exp,
            "wfe_ratio_pct": wfe_ratio_pct,
            "is_robust": is_robust,
            "overfit_warning": not is_robust
        }
