import logging
from datetime import datetime, timezone
from typing import Dict, Any
from session_management.managers.session_manager import SessionManager
from session_management.health.provider_health_checker import ProviderHealthChecker

# Import P2 adapters
from integrations.nse_adapter import NSEAdapter
from integrations.screener_adapter import ScreenerAdapter
from integrations.chartink_adapter import ChartinkAdapter
from integrations.tradingview_adapter import TradingViewAdapter
from operational_layer.kite_registry_adapter import KiteRegistryAdapter

logger = logging.getLogger("CentralHealthAggregator")

class CentralHealthAggregator:
    """
    Aggregates session health across all primary peripheral providers:
    NSE, Screener, Chartink, TradingView, and Kite.
    """
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.health_checker = ProviderHealthChecker(session_manager)
        
        # Initialize standard adapters with read-only governance
        self.adapters = {
            "nse_provider": NSEAdapter(),
            "screener_provider": ScreenerAdapter(),
            "chartink_provider": ChartinkAdapter(),
            "tradingview_provider": TradingViewAdapter(),
            "kite_provider": KiteRegistryAdapter()
        }

        # Register providers in session manager
        for pid in self.adapters.keys():
            self.session_manager.register_provider(pid)

    def refresh_all_health(self) -> Dict[str, Any]:
        """Runs health checks across all registered providers and returns consolidated status."""
        results = {}
        for pid, adapter in self.adapters.items():
            session_meta = self.health_checker.evaluate_adapter(pid, adapter)
            results[pid] = session_meta.model_dump(mode="json")
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "providers": results
        }
