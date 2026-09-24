"""
Base Strategy Runner Interface.
Enforces preparation, evaluation, and position management boundaries.
"""
class StrategyBase:
    def __init__(self, name: str):
        self.name = name

    def prepare(self, data) -> None:
        raise NotImplementedError

    def on_bar(self, bar_index: int, current_bar, history) -> dict:
        raise NotImplementedError
