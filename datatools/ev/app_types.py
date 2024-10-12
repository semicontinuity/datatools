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


class Realm:
    name: str

    def __init__(self, name):
        self.name = name

    def create_view(self, e_ref: EntityReference) -> View:
        pass
