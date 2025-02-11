from datatools.dbview.x.util.pg import get_where_clauses0
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause


def resolve_selector(base_path: str, rest: str) -> DbTableRowsSelector:
    i = rest.find('/')
    if i == -1:
        raise ValueError()
    table = rest[:i]
    clauses = get_where_clauses0(base_path + '/' + table, rest[(i + 1):])
    return DbTableRowsSelector(table=table, where=[DbSelectorClause(*w) for w in clauses])