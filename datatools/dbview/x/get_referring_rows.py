#!/usr/bin/env python3
import json
from collections import defaultdict
from typing import Tuple, List

from datatools.dbview.util.pg import get_table_pks, execute_sql, get_table_foreign_keys_inbound, describe_table
from datatools.dbview.x.util.pg import connect_to_db, get_env, get_where_clauses
from datatools.json.util import to_jsonisable
from datatools.util.logging import debug


def get_pk_and_text_values_for_selected_rows(conn, table: str, selector_column_name: str, selector_column_value: str) -> Tuple[List, List]:
    d = describe_table(conn, table)
    text_columns = [row['column_name'] for row in d if row['data_type'] == 'text']

    table_pks = get_table_pks(conn, table)
    if len(table_pks) == 0:
        raise Exception(f"expected PKs in table {table}")

    columns = table_pks + text_columns

    sql = f"SELECT {', '.join(columns)} from {table} where {selector_column_name}={selector_column_value}"
    debug(sql)
    rows = execute_sql(conn, sql)
    return [{k: to_jsonisable(v) for k, v in row.items() if k in table_pks} for row in rows], [{k: to_jsonisable(v) for k, v in row.items() if k not in table_pks} for row in rows]


def make_referring_rows_model(conn, table: str, where: List[Tuple[str, str, str]]):
    debug('make_referring_rows_model', table=table, where=where)

    if not where:
        raise Exception('WHERE clause is required')
    if len(where) != 1:
        raise Exception('WHERE clauses must contain 1 clause')

    where_column, where_op, where_value = where[0]
    if where_op != '=':
        raise Exception('WHERE clause must be PK equality')

    result = defaultdict(lambda: defaultdict(list))

    inbound_relations = get_table_foreign_keys_inbound(conn, table)
    for inbound_relation in inbound_relations:
        this_table = inbound_relation['foreign_table_name']
        if table != this_table:
            raise Exception('illegal state')

        this_column = inbound_relation['foreign_column_name']

        if this_column != where_column:
            sql = f"SELECT {this_column} from {table} where {where_column} {where_op} {where_value}"
            debug(sql)
            rows = execute_sql(conn, sql)
            if len(rows) != 1:
                raise Exception(f'illegal state: expected 1 row, but was {len(rows)}')
            selector_value = "'" + rows[0][this_column] + "'"
        else:
            selector_value = where_value

        foreign_table = inbound_relation['table_name']
        foreign_column = inbound_relation['column_name']

        pk_kv, text_kv = get_pk_and_text_values_for_selected_rows(conn, foreign_table, foreign_column, selector_value)
        if len(pk_kv) == 0:
            continue
        else:
            entry = []
            result[foreign_table][foreign_column] = entry
            for i in range(len(pk_kv)):
                entry.append(
                    {
                        'key': pk_kv[i],
                        'value': text_kv[i],
                    }
                )

    return result


def main():
    table = get_env('TABLE')
    where = get_where_clauses()

    with connect_to_db() as conn:
        print(json.dumps(make_referring_rows_model(conn, table, where)))


if __name__ == '__main__':
    main()
