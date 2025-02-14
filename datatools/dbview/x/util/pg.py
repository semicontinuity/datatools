import os
from typing import List, Tuple
from os.path import isdir, join


def get_sql() -> str:
    table = get_env('TABLE')
    where = get_where_clause()
    sql = f'SELECT * from {table}'
    if where:
        sql += f' where {where}'
    return sql


def get_env(key):
    value = os.getenv(key)
    if value is None:
        raise Exception(f'Must set {key}')
    return value


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
                pack_name = parts[i]
                path.append(pack_name)
                i += 1

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
