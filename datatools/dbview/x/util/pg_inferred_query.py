import os
from os.path import isdir, join

import yaml

from datatools.dbview.x.util.db_query import DbQuery, DbQueryFilterClause
from datatools.dbview.x.util.helper import get_required_prop
from datatools.util.dataclasses import dataclass_from_dict


def inferred_query(props) -> DbQuery:
    ctx_dir = props.get('CTX_DIR')
    ctx_base = props.get('CTX_BASE')
    ctx_base_parts = [] if ctx_base is None else ctx_base.split('/')
    rest = props.get('__REST') or ''

    if query := props.get('QUERY'):
        query_d = yaml.safe_load(query)
        return dataclass_from_dict(DbQuery, query_d)
    else:
        base_path = ctx_dir + '/' + '/'.join(ctx_base_parts)
        return inferred_query_from(props, base_path, rest)


def inferred_query_from(props, base_path, rest):
    clauses = get_where_clauses1(base_path, rest)
    return DbQuery(
        table=get_required_prop('TABLE', props),
        filter=[
            DbQueryFilterClause(
                column=column,
                op=op,
                value=value,
            ) for column, op, value in clauses
        ]
    )


def get_where_clauses1(table_path: str, rest: str) -> list[tuple[str, str, str]]:
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
                clauses.append((field, 'in', sub_folders))
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

                clauses.append((field, 'in', values))
            else:
                # FS structure like :field_name/field_value
                clauses.append((field, '=', value))

        elif key.startswith('='):
            if i >= len(parts):
                break
            value = parts[i]
            path.append(value)
            i += 1
            clauses.append((key.removeprefix('='), '=', value))
        elif key.startswith('+'):
            clauses.append((key.removeprefix('+'), 'is not', None))
        elif key.startswith('-'):
            clauses.append((key.removeprefix('-'), 'is', None))

    return clauses
