from types import NoneType
from typing import Any

import yaml

from datatools.dbview.x.util.db_query import DbQuery, DbQueryFilterClause, DbQuerySelector
from datatools.dbview.x.util.helper import get_env


def get_sql() -> str:
    return query_to_string(yaml.safe_load(get_env('QUERY')))


def query_to_string(query: DbQuery, table: str = None) -> str:
    table = table or query.table

    # selectors = query.get('selectors')
    # selectors_str = ',\n'.join(selector_to_string(s, table) for s in selectors) if selectors else '*'
    selectors = query.selectors
    selectors_str = query_selectors_to_string(selectors, table)

    filter_str = query_filter_to_string(query.filter)

    return f"""select

{selectors_str}
   
from {table} __{table}

{"where" if filter_str else ""}
{filter_str}    
"""


def query_selectors_to_string(selectors, table):
    return ',\n'.join(selector_to_string(s, table) for s in selectors) if selectors else '*'


def query_filter_to_string(clauses: list[DbQueryFilterClause]):
    return '\nand\n'.join(_filter_clause_to_string(c) for c in clauses) if clauses else ''


def selector_to_string(selector: DbQuerySelector, table: str) -> str:
    column = selector.column

    if resolve := selector.resolve:
        foreign_table = resolve.table
        foreign_key = resolve.column or column
        alias = resolve.alias or foreign_table
        return f"(select {resolve.select} as {alias} from {foreign_table} where {foreign_key} = __{table}.{column})"
    else:
        return column


def _filter_clause_to_string(clause: DbQueryFilterClause) -> str:
    return f"{clause.column} {clause.op} {value_to_string(clause.value)}"


def value_to_string(value: Any) -> str:
    if type(value) is NoneType:
        return 'null'
    elif type(value) is list:
        return '(' + ','.join(value_to_string(v) for v in value) + ')'
    else:
        return repr(value)
