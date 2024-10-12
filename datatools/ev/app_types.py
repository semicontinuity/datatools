from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class Realm:
    name: str
    properties: Dict[str, str]


@dataclass
class EntityReference:
    pass


@dataclass
class View:
    def build(self):
        pass

    def run(self) -> Optional[EntityReference]:
        pass
