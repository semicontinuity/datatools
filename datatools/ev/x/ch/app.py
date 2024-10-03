#!/usr/bin/env python3
import json
import os

from datatools.dbview.x.util.pg import get_where_clauses
from datatools.json.util import to_jsonisable

import clickhouse_connect


def main():
    hostname = os.environ['YC_CH_HOST']
    database = os.environ['YC_CH_DATABASE']
    user = os.environ['YC_CH_USER']
    password = os.environ['YC_CH_PASSWORD']
    table = os.environ['TABLE']

    where_clause = get_where_clauses()[-1]
    column, op, value = where_clause
    query = f"select * from {table} where {column} {op} {value}"

    client = clickhouse_connect.get_client(
        host=hostname,
        port=8443,
        secure=True,
        verify=False,
        username=user,
        password=password,
        database=database
    )
    result = client.query(query)
    res = [
        {column_name: row1[i] for i, column_name in enumerate(result.column_names)}
        for row1 in result.result_rows
    ]

    for row in res:
        print(json.dumps(to_jsonisable({k: to_jsonisable(v) for k, v in row.items()})))


if __name__ == '__main__':
    main()
