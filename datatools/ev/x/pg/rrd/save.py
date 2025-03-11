#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

from x.util.pg import execute_sql

from datatools.dbview.x.util.pg import infer_query, make_result_set_metadata
from datatools.dbview.x.util.pg_query import query_to_string
from datatools.ev.entity_transfer import write_entity_parts_s
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.json.util import to_jsonisable


def main():
    query = infer_query(os.environ)
    wd = Path(os.environ['PWD'])

    with PgDataSource(os.environ).connect_to_db() as conn:
        write_entity_parts_s(
            wd, json.dumps(to_jsonisable(query), indent=2),
            jsonl(execute_sql(conn, query_to_string(query))),
            json.dumps(to_jsonisable(make_result_set_metadata(conn, query)), indent=2)
        )


def jsonl(j):
    return ''.join(json.dumps(to_jsonisable(row), ensure_ascii=False) + '\n' for row in j)


if __name__ == '__main__':
    sys.exit(main() or 0)
