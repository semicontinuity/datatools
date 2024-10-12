#!/usr/bin/env python3
from typing import Tuple, List

from datatools.dbview.util.pg import execute_sql, describe_table
from datatools.json.util import to_jsonisable
from datatools.util.logging import debug


def get_pk_and_text_values_for_selected_rows(
        conn, table: str, selector_column_name: str, selector_column_value: str, table_pks: List, limit: int = 20
) -> Tuple[List, List]:
    d = describe_table(conn, table)
    text_columns = [row['column_name'] for row in d if row['data_type'] == 'text']

    columns = table_pks + text_columns

    sql = f"SELECT {', '.join(columns)} from {table} where {selector_column_name}={selector_column_value} limit {limit}"
    debug(sql)
    rows = execute_sql(conn, sql)
    return [{k: to_jsonisable(v) for k, v in row.items() if k in table_pks} for row in rows], [{k: to_jsonisable(v) for k, v in row.items() if k not in table_pks} for row in rows]


def get_selector_value(conn, inbound_relation, table, where):
    this_column = inbound_relation['foreign_column_name']
    where_column, where_op, where_value = where[0].column, where[0].op, where[0].value
    if where_op != '=':
        raise Exception('WHERE clause must be PK equality')
    if this_column != where_column:
        sql = f"SELECT {this_column} from {table} where {where_column} {where_op} {where_value}"
        debug(sql)
        rows = execute_sql(conn, sql)
        if len(rows) != 1:
            raise Exception(f'illegal state: expected 1 row, but was {len(rows)}')
        selector_value = "'" + rows[0][this_column] + "'"
    else:
        selector_value = where_value
    return selector_value
