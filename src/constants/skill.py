from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SkillRequirement:
    name: str
    requirement: str

class Skills:
    def __init__(self, config: Dict):
        self._skills = config['skills']['list']
        self._requirements = {
            name: SkillRequirement(name, req)
            for name, req in config['skills']['requirements'].items()
        }

    @property
    def all_skills(self) -> List[str]:
        return self._skills

    def get_requirement(self, skill: str) -> SkillRequirement:
        return self._requirements[skill]