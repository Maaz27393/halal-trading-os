from typing import Dict, Any
from macro.adapters.macro_adapter import DomainMacroAdapter

class MacroHealthChecker:
    def __init__(self, adapter: DomainMacroAdapter):
        self.adapter = adapter

    def check(self) -> Dict[str, Any]:
        return self.adapter.health()
