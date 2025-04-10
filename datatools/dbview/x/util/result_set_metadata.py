from dataclasses import dataclass
from typing import List

from datatools.dbview.x.util.relation import Relation


@dataclass
class ResultSetMetadata:
    table: str
    primaryKeys: List[str]
    relations: List[Relation]

    def fk_names(self):
        return {r.src.name for r in self.relations if r.src.qualifier == self.table}