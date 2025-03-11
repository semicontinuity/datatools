from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class QualifiedName:
    qualifier: str
    name: str


@dataclass
class Relation:
    src: QualifiedName
    dst: QualifiedName


@dataclass
class ResultSetMetadata:
    table: str
    primaryKeys: List[str]
    relations: List[Relation]