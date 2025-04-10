from dataclasses import dataclass
from typing import List

from datatools.dbview.x.util.relation import Relation


@dataclass
class ResultSetMetadata:
    table: str
    primaryKeys: List[str]
    relations: List[Relation]
