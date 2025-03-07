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
    realm_ctx: str = None
    realm_ctx_dir: str = None

    def __init__(self, name, realm_ctx: str = None, realm_ctx_dir: str = None):
        self.name = name
        self.realm_ctx = realm_ctx
        self.realm_ctx_dir = realm_ctx_dir

    def create_view(self, e_ref: EntityReference) -> View:
        pass
