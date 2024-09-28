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

    res = fetch(hostname, database, user, password, table, where_clause)

    for row in res:
        print(json.dumps(to_jsonisable({k: to_jsonisable(v) for k, v in row.items()})))


def fetch(hostname, database, user, password, table, where_clause):
    client = clickhouse_connect.get_client(
        host=hostname,
        port=8443,
        secure=True,
        verify=False,
        username=user,
        password=password,
        database=database
    )
    column, op, value = where_clause
    result = client.query(f"select * from {table} where {column} {op} {value}")
    res = []
    for row in result.result_rows:
        res.append({column_name: row[i] for i, column_name in enumerate(result.column_names)})
    return res


if __name__ == '__main__':
    main()
