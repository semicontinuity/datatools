from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class EntityReference:
    realm_name: str


@dataclass
class View:
    def build(self):
        pass

    def run(self) -> Optional[EntityReference]:
        pass
