#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

from x.util.pg import get_table_foreign_keys_all, get_table_pks, execute_sql

from datatools.dbview.x.util.pg import infer_query
from datatools.dbview.x.util.pg_query import query_to_string
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.rrd.model import Relation, QualifiedName, ResultSetMetadata
from datatools.json.util import to_jsonisable


def main():
    query = infer_query(os.environ)
    wd = Path(os.environ['PWD'])

    with PgDataSource(os.environ).connect_to_db() as conn:
        if not (wd / '.query').exists():
            write_file(
                wd / '.query', json.dumps(to_jsonisable(query), indent=2)
            )

        write_file(
            wd / 'content.jsonl', jsonl(execute_sql(conn, query_to_string(query)))
        )

        write_file(
            wd / 'rs-metadata.json', json.dumps(to_jsonisable(make_result_set_metadata(conn, query)), indent=2)
        )


def write_file(name, s):
    with open(name, 'w') as f:
        f.write(s)


def jsonl(j):
    return ''.join(json.dumps(to_jsonisable(row), ensure_ascii=False) + '\n' for row in j)


def make_result_set_metadata(conn, query) -> ResultSetMetadata:
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


if __name__ == '__main__':
    sys.exit(main() or 0)
