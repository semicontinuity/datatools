import yaml

from datatools.dbview.x.util.pg import get_env


def get_sql() -> str:
    query = yaml.safe_load(get_env('QUERY'))
    # return str(query)
    return query_to_string(query)


def query_to_string(query: dict) -> str:
    table = query['table']

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
    return f"{clause['field']} {clause['op']} '{clause['value']}'"