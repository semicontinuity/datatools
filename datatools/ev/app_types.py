from dataclasses import dataclass
from typing import Optional


@dataclass
class EntityReference:
    pass


@dataclass
class View:
    def build(self):
        pass

    def run(self) -> Optional[EntityReference]:
        pass
