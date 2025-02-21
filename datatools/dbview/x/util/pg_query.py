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
    selectors_str = ',\n'.join(selector_to_string(s, table) for s in selectors) if selectors else '*'

    clauses = query.filter
    filter_str = '\nand\n'.join(filter_to_string(c) for c in clauses) if clauses else ''

    return f"""select

{selectors_str}
   
from {table} __{table}

{"where" if filter_str else ""}
{filter_str}    
"""
# def query_to_string(query: dict, table: str = None) -> str:
#     table = table or query['table']
#
#     selectors = query.get('selectors')
#     selectors_str = ',\n'.join(selector_to_string(s, table) for s in selectors) if selectors else '*'
#
#     clauses = query.get('filter')
#     filter_str = '\nand\n'.join(filter_to_string(c) for c in clauses) if clauses else ''
#
#     return f"""select
#
# {selectors_str}
#
# from {table} __{table}
#
# {"where" if filter_str else ""}
# {filter_str}
# """


def selector_to_string(selector: DbQuerySelector, table: str) -> str:
    column = selector.column

    if resolve := selector.resolve:
        foreign_table = resolve.table
        foreign_key = resolve.column or column
        alias = resolve.alias or foreign_table
        return f"(select {resolve.select} as {alias} from {foreign_table} where {foreign_key} = __{table}.{column})"
    else:
        return column
# def selector_to_string(selector: dict, table: str) -> str:
#     column = selector['column']
#
#     if resolve := selector.get('resolve'):
#         foreign_table = resolve['table']
#         foreign_key = resolve.get('column') or column
#         alias = resolve.get('alias') or foreign_table
#         return f"(select {resolve['select']} as {alias} from {foreign_table} where {foreign_key} = __{table}.{column})"
#     else:
#         return column


def filter_to_string(clause: DbQueryFilterClause) -> str:
    return f"{clause.column} {clause.op} {value_to_string(clause.value)}"
# def filter_to_string(clause: dict) -> str:
#     return f"{clause['field']} {clause['op']} {value_to_string(clause['value'])}"


def value_to_string(value: Any) -> str:
    if type(value) is NoneType:
        return 'null'
    elif type(value) is list:
        return '(' + ','.join(value_to_string(v) for v in value) + ')'
    else:
        return repr(value)
