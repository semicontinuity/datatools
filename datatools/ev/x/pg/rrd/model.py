from dataclasses import dataclass
from typing import Any, List


@dataclass
class CardData:
    table: str
    pks: list[str]
    rows: list[dict[str, Any]]


@dataclass
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
