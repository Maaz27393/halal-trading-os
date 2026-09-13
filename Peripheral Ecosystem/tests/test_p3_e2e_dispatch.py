import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contracts import ExecutionIntent, TransactionType, OrderType, ProductType, MarketQuote
from integrations.fallback_adapters import BackupNSEAdapter
from integrations.simulated_broker import SimulatedBrokerAdapter
from security.order_validator import OrderValidator
from security.gateway import PermissionGateway
from security.execution_gateway import ExecutionPolicyGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION

def run_e2e_dispatch_workflow():
    print("Initializing P3.6 - End-to-End Paper/Shadow Dispatch Workflow...")

    # 1. Verify frozen governance guardrail
    assert LIVE_AUTO_EXECUTION is False, "Safety Violation: LIVE_AUTO_EXECUTION must remain False!"
    print("Governance Check: LIVE_AUTO_EXECUTION = False verified.")

    # 2. Initialize Data Ingestion Layer (Phase 2 Backup Adapter)
    data_adapter = BackupNSEAdapter()
    data_adapter.connect()
    
    # Simulate fetching live market quote for RELIANCE
    raw_quote = data_adapter.read("RELIANCE")
    canonical_quote = data_adapter.normalize(raw_quote, MarketQuote)
    print(f"Data Ingestion Complete — RELIANCE Last Price: ₹{canonical_quote.last_price}")
    data_adapter.disconnect()

    # 3. Initialize Execution Infrastructure (Phase 3 Gateway & Broker)
    broker = SimulatedBrokerAdapter()
    broker.connect()

    validator = OrderValidator(max_capital_per_order=300000.0)
    perm_gateway = PermissionGateway()
    perm_gateway.grant_permission("ema_strategy_agent", "EXECUTE")

    policy_gateway = ExecutionPolicyGateway(
        broker=broker,
        validator=validator,
        permission_gateway=perm_gateway
    )

    # 4. Formulate Execution Intent based on market quote
    intent = ExecutionIntent(
        source_provider="ema_strategy_agent",
        strategy_id="EMA_CROSSOVER_V1",
        symbol=canonical_quote.symbol,
        transaction_type=TransactionType.BUY,
        order_type=OrderType.MARKET,
        product=ProductType.MIS,
        quantity=50,  # 50 * 2852.0 = 142,600 (Well within 300k limit)
        stop_loss=2800.0,
        target=2950.0,
        idempotency_key="E2E_DISPATCH_UUID_8899"
    )

    # 5. Execute via Policy Gateway (Permission -> Validation -> Shadow Dispatch)
    print("Dispatching Execution Intent through Policy Gateway...")
    response = policy_gateway.execute(
        intent=intent,
        current_market_price=canonical_quote.last_price,
        caller_role="ema_strategy_agent"
    )

    print(f"Shadow Dispatch Response: {response.model_dump()}")
    assert response.status == "COMPLETE"
    assert response.broker_order_id.startswith("SIM_")

    broker.disconnect()
    print("P3.6 End-to-End Paper/Shadow Dispatch Workflow Passed Successfully!")

if __name__ == "__main__":
    run_e2e_dispatch_workflow()