"""
Strategy Interface Contract.
Defines the lifecycle methods for backtestable strategies (prepare, evaluate, generate_signal, manage_position).
"""
class BaseStrategy:
    def prepare(self, bars) -> None:
        pass

    def evaluate(self, context) -> dict:
        pass

    def generate_signal(self, context) -> dict:
        pass

    def manage_position(self, position, context) -> dict:
        pass
