#!/usr/bin/env python3
import json
from collections import defaultdict

from datatools.dbview.util.pg import get_table_pks, execute_sql, get_table_foreign_keys_inbound
from datatools.dbview.x.util.pg import connect_to_db, get_env, get_where_clauses
from datatools.util.logging import debug
from datatools.json.util import to_jsonisable


def get_pk_values_for_selected_rows(conn, table: str, selector_column_name: str, selector_column_value: str):
    table_pks = get_table_pks(conn, table)
    if len(table_pks) == 0:
        raise Exception(f"expected PKs in table {table}")

    sql = f"SELECT {', '.join(table_pks)} from {table} where {selector_column_name}={selector_column_value}"
    debug(sql)
    rows = execute_sql(conn, sql)
    debug(len(rows))
    return [{k: to_jsonisable(v) for k, v in row.items()} for row in rows]


def main():
    with connect_to_db() as conn:
        table = get_env('TABLE')
        where = get_where_clauses()
        if not where:
            raise Exception('WHERE clause is required')
        if len(where) != 1:
            raise Exception('WHERE clauses must contain 1 clause')

        where_column, where_op, where_value = where[0]
        if where_op != '=':
            raise Exception('WHERE clause must be PK equality')

        result = defaultdict(dict)

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
            debug(selector_value)

            foreign_table = inbound_relation['table_name']
            foreign_column = inbound_relation['column_name']

            rows = get_pk_values_for_selected_rows(conn, foreign_table, foreign_column, selector_value)
            if len(rows) == 0:
                continue
            else:
                result[foreign_table][foreign_column] = rows

        print(json.dumps(result))


if __name__ == '__main__':
    main()
