#!/usr/bin/env python3
import json
import os

from datatools.dbview.x.util.pg import get_where_clauses
from datatools.json.util import to_jsonisable


def main():
    import clickhouse_connect

    CLICKHOUSE_CLOUD_HOSTNAME = os.environ['YC_CH_HOST']
    CLICKHOUSE_CLOUD_USER = os.environ['YC_CH_USER']
    CLICKHOUSE_CLOUD_PASSWORD = os.environ['YC_CH_PASSWORD']
    CLICKHOUSE_CLOUD_DATABASE = os.environ['YC_CH_DATABASE']

    client = clickhouse_connect.get_client(
        host=CLICKHOUSE_CLOUD_HOSTNAME,
        port=8443,
        secure=True,
        verify=False,
        username=CLICKHOUSE_CLOUD_USER,
        password=CLICKHOUSE_CLOUD_PASSWORD,
        database=CLICKHOUSE_CLOUD_DATABASE
    )

    column, op, value = get_where_clauses()[-1]
    result = client.query(f"select * from cdr where {column} {op} {value}")

    rows = result.result_rows
    if len(rows) != 1:
        return
    print(json.dumps(to_jsonisable(rows[0]), indent=2))


if __name__ == '__main__':
    main()