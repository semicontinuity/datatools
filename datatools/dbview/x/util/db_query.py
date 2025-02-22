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


# Use List (not list) because of dataclass_from_dict
@dataclass
class DbQuery:
    table: str|None
    filter: List[DbQueryFilterClause]
    selectors: List[DbQuerySelector] = None

    def with_more_filter_clauses(self, filter_clauses: list[DbQueryFilterClause]):
        return self.with_filter_clauses(self.filter + filter_clauses)

    def with_filter_clauses(self, filter_clauses: list[DbQueryFilterClause]):
        return DbQuery(
            table=self.table,
            filter=filter_clauses,
            selectors=self.selectors,
        )
