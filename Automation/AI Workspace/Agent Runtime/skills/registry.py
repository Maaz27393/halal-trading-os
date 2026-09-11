import sys
from pathlib import Path
from typing import Dict, Any, Optional

skills_path = Path(__file__).parent
if str(skills_path) not in sys.path:
    sys.path.append(str(skills_path))

from base_skill import BaseSkill

class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        self._skills[skill.name] = skill

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        return self._skills.get(name)

    def get_skills_for_intent(self, intent: str) -> Dict[str, BaseSkill]:
        return {
            name: skill for name, skill in self._skills.items()
            if skill.required_intent == intent
        }

    def execute_skill(self, skill_name: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        skill = self.get_skill(skill_name)
        if not skill:
            return {"status": "ERROR", "message": f"Skill '{skill_name}' not found in registry."}
        return skill.execute(context, **kwargs)
