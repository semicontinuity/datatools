from dataclasses import dataclass

from datatools.dbview.share.app_types import EntityReference


@dataclass
class RestEntity(EntityReference):
    url: str
