from dataclasses import dataclass

from datatools.ev.app_types import EntityReference
from datatools.ev.x.pg.types import DbTableRowsSelector


@dataclass(kw_only=True)
class ClickhouseRowEntity(EntityReference):
    selector: DbTableRowsSelector
