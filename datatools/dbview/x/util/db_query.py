from dataclasses import dataclass
from typing import Any, List


@dataclass
class DbQueryFilterClause:
    column: str
    op: str
    value: Any


@dataclass
class DbQuerySelectorResolve:
    table: str
    select: str
    column: str = None
    alias: str = None


@dataclass
class DbQuerySelector:
    column: str
    resolve: DbQuerySelectorResolve = None


@dataclass
class DbQuery:
    table: str|None
    filter: List[DbQueryFilterClause]
    selectors: List[DbQuerySelector] = None
