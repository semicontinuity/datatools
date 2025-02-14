from typing import Tuple, List

from datatools.dbview.x.util.pg import get_where_clauses0
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause


def resolve_selector_from_paths(base_path: str, rest: str) -> DbTableRowsSelector:
    table, clauses = resolve_table_and_clauses(base_path, rest)
    return DbTableRowsSelector(table=table, where=[DbSelectorClause(*w) for w in clauses])


def resolve_table_and_clauses(base_path: str, rest: str) -> Tuple[str, List[Tuple[str, str, str]]]:
    i = rest.find('/')
    if i == -1:
        raise ValueError()
    table = rest[:i]
    clauses = get_where_clauses0(base_path + '/' + table, rest[(i + 1):])
    return table, clauses
