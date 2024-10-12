from dataclasses import dataclass
from typing import Dict

from datatools.ev.app_types import EntityReference


@dataclass
class RestEntity(EntityReference):
    concept: str
    # entity_id: str
    variables: Dict[str, str]
