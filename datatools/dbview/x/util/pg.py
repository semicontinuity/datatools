import os
from os.path import isdir, join
from typing import List, Tuple

from x.util.pg import get_table_pks, get_table_foreign_keys_all

from datatools.dbview.x.util.db_query import DbQuery
from datatools.dbview.x.util.helper import get_required_prop
from datatools.dbview.x.util.pg_inferred_query import inferred_query
from datatools.dbview.x.util.pg_query import query_to_string, query_from_yaml
from datatools.dbview.x.util.result_set_metadata import ResultSetMetadata
from datatools.dbview.x.util.relation import Relation
from datatools.dbview.x.util.qualified_name import QualifiedName
from datatools.util.logging import debug


def get_sql() -> str:
    q = infer_query(os.environ)
    debug('get_sql', query=q)
    return query_to_string(q)


def infer_query(props) -> DbQuery:
    if query := props.get('QUERY'):
        q = query_from_yaml(query)
    else:
        q = inferred_query(props)
    if not q.table:
        q.table = get_required_prop('TABLE', props)
    return q


def __inferred_select_sql(table):
    where = get_where_clause()
    sql = f'SELECT * from {table}'
    if where:
        sql += f' where {where}'
    return sql


def get_where_clause():
    return '\n and \n'.join(f'{a} {op} {b}' for a, op, b in get_where_clauses())


def get_where_clauses() -> List[Tuple[str, str, str]]:
    return get_where_clauses_from_props(os.environ)


def get_where_clauses_from_props(p) -> List[Tuple[str, str, str]]:
    ctx_dir = p.get('CTX_DIR')
    ctx_base = p.get('CTX_BASE')
    ctx_base_parts = [] if ctx_base is None else ctx_base.split('/')

    rest = p.get('__REST') or ''

    return get_where_clauses0(ctx_dir + '/' + '/'.join(ctx_base_parts), rest)


def get_where_clauses0(table_path: str, rest: str) -> List[Tuple[str, str, str]]:
    parts = rest.split('/') if rest != '' else []

    i = 0
    clauses = []
    path = []

    while True:
        if i >= len(parts):
            break
        key = parts[i]
        path.append(key)
        i += 1

        if key.startswith(':'):
            field = key.removeprefix(':')
            if i >= len(parts):
                folder = table_path + '/' + '/'.join(path)
                sub_folders = [f for f in os.listdir(folder) if isdir(join(folder, f))]
                clauses.append((field, 'in', ('(\n' + ',\n'.join(map(repr, sub_folders)) + '\n)')))
                break

            value = parts[i]
            path.append(value)
            i += 1

            if value == '@':
                #print('path', path, file=sys.stderr)
                # FS structure like :field_name/@/name_of_pack/@: @ contains a list of values
                #values = os.environ['IN']
                values_file = table_path + '/' + '/'.join(path) + '/' + '@'
                with open(values_file) as f:
                    values = f.read().split('\n')
                values = [v for v in values if v != '']

                clauses.append((field, 'in', ('(\n' + ',\n'.join(map(repr, values)) + '\n)')))
            else:
                # FS structure like :field_name/field_value
                clauses.append((field, '=', repr(value)))

        elif key.startswith('='):
            if i >= len(parts):
                break
            value = parts[i]
            path.append(value)
            i += 1
            clauses.append((key.removeprefix('='), '=', repr(value)))
        elif key.startswith('+'):
            clauses.append((key.removeprefix('+'), 'is not', 'null'))
        elif key.startswith('-'):
            clauses.append((key.removeprefix('-'), 'is', 'null'))

    return clauses


def make_result_set_metadata(conn, query: DbQuery) -> ResultSetMetadata:
    return ResultSetMetadata(
        table=query.table,
        primaryKeys=get_table_pks(conn, query.table),
        relations=relations(conn, query.table),
    )


def relations(conn, table: str) -> list[Relation]:
    return [
        Relation(
            src=QualifiedName(edge['table_name'], edge['column_name']),
            dst=QualifiedName(edge['foreign_table_name'], edge['foreign_column_name']),
        ) for edge in get_table_foreign_keys_all(conn, table)
    ]