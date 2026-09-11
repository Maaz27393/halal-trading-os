from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseSkill(ABC):
    name: str
    description: str
    required_intent: str
    allowed_tools: List[str]

    @abstractmethod
    def execute(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute skill workflow and return structured outcome."""
        pass
