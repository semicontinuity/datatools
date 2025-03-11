#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

from x.util.pg import get_table_foreign_keys_all, get_table_pks, execute_sql

from datatools.dbview.x.util.pg import infer_query
from datatools.dbview.x.util.pg_query import query_to_string
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.json.util import to_jsonisable


def main():
    query = infer_query(os.environ)
    wd = Path(os.environ['PWD'])

    with PgDataSource(os.environ).connect_to_db() as conn:

        if not (wd / '.query').exists():
            write_file(
                wd / '.query', json.dumps(to_jsonisable(query), indent=2))

        write_file(
            wd / 'contents.jsonl', jsonl(execute_sql(conn, query_to_string(query))))

        write_file(
            wd / 'rs-metadata.json', json.dumps(make_result_set_metadata(conn, query), indent=2))


def write_file(name, s):
    with open(name, 'w') as f:
        f.write(s)


def jsonl(j):
    return ''.join(json.dumps(to_jsonisable(row), ensure_ascii=False) + '\n' for row in j)


def make_result_set_metadata(conn, query):
    return {
        'table': query.table,
        'table-primary-keys': get_table_pks(conn, query.table),
        'table-relations': relations(conn, query.table)
    }


def relations(conn, table: str):
    edges = get_table_foreign_keys_all(conn, table)
    res = []
    for edge in edges:
        src_table = edge['table_name']
        src_column = edge['column_name']
        dst_table = edge['foreign_table_name']
        dst_column = edge['foreign_column_name']

        entry = {
            'table_name': src_table,
            'column_name': src_column,
            'foreign_table_name': dst_table,
            'foreign_column_name': dst_column,
        }
        res.append(entry)
    return res


if __name__ == '__main__':
    sys.exit(main() or 0)
