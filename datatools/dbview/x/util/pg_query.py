import yaml

from datatools.dbview.x.util.helper import get_env


def get_sql() -> str:
    return query_to_string(yaml.safe_load(get_env('QUERY')))


def query_to_string(query: dict, table: str = None) -> str:
    table = table or query['table']

    selectors = query.get('selectors')
    selectors_str = ',\n'.join(selector_to_string(s, table) for s in selectors) if selectors else '*'

    clauses = query.get('filter')
    filter_str = '\nand\n'.join(filter_to_string(c) for c in clauses) if clauses else ''

    return f"""select

{selectors_str}
   
from {table} __{table}

{"where" if filter_str else ""}
{filter_str}    
"""


def selector_to_string(selector: dict, table: str) -> str:
    field = selector['field']

    if resolve := selector.get('resolve'):
        foreign_table = resolve['table']
        foreign_key = resolve.get('field') or field
        alias = resolve.get('as') or foreign_table
        return f"(select {resolve['select']} as {alias} from {foreign_table} where {foreign_key} = __{table}.{field})"
    else:
        return field


def filter_to_string(clause: dict) -> str:
    value = clause['value']
    value_str = '(' + ','.join(repr(v) for v in value) + ')' if type(value) is list else repr(value)

    return f"{clause['field']} {clause['op']} {value_str}"
