from typing import Any


def describe_table(conn, table: str):
    return execute_sql(conn, describe_table_sql(table))


def describe_table_sql(table: str):
    return f'''select

column_name,
data_type,
character_maximum_length,
column_default,
is_nullable

from

INFORMATION_SCHEMA.COLUMNS

where table_name = '{table}';'''


def get_table_pks(conn, table: str) -> list[str]:
    return [row['column_name'] for row in execute_sql(conn, get_table_pks_sql(table))]


def get_table_pks_sql(table: str):
    return f'''SELECT c.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
    JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
      AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
    WHERE constraint_type = 'PRIMARY KEY' and tc.table_name = '{table}';
    '''


def get_table_foreign_keys_outbound(conn, table: str):
    """
    Returns list of dicts with keys:
    - table_name
    - column_name
    - foreign_table_name
    - foreign_column_name
    """
    return execute_sql(conn, get_table_foreign_keys_outbound_sql(table))


def get_table_foreign_keys_outbound_sql(table: str):
    return f'''
with fkeys as (

SELECT
    tc.constraint_name,

    tc.table_name,
    kcu.column_name,

    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM
    information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage
        AS kcu
        ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage
        AS ccu
        ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY'

)

select * from fkeys where table_name='{table}' order by 1
        '''


def get_table_foreign_keys_inbound_tuples(conn, table: str):
    return [(row['table_name'], row['column_name']) for row in execute_sql(conn, get_table_foreign_keys_inbound_sql(table))]


def get_table_foreign_keys_inbound(conn, table: str):
    """
    Returns list of dicts with keys:
    - column_name
    - table_name
    - foreign_table_name
    - foreign_column_name
    """
    return execute_sql(conn, get_table_foreign_keys_inbound_sql(table))


def get_table_foreign_keys_inbound_sql(table: str):
    return f'''
SELECT
    tc.table_schema,
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    
WHERE tc.constraint_type = 'FOREIGN KEY'
AND ccu.table_name='{table}'

ORDER BY tc.table_schema, tc.table_name
        '''


def get_table_foreign_keys_inbound_from(conn, from_table: str, to_table: str):
    """
    Returns list of dicts with keys:
    - column_name
    - table_name
    - foreign_table_name
    - foreign_column_name
    """
    return execute_sql(conn, get_table_foreign_keys_inbound_from_sql(from_table, to_table))


def get_table_foreign_keys_inbound_from_sql(from_table: str, to_table: str):
    return f'''
SELECT
    tc.table_schema,
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'

    AND ccu.table_name='{to_table}'
    AND tc.table_name='{from_table}'
        '''


def execute_sql(conn, sql: str) -> list[dict[str, Any]]:
    q = conn.cursor()
    q.execute(sql)

    column_names = [i.name for i in q.description]
    result = []

    while True:
        row_tuple = q.fetchone()
        if row_tuple is None:
            break

        row = {}
        i = 0

        for column_name in column_names:
            row[column_name] = row_tuple[i]
            i += 1

        result.append(row)

    q.close()

    return result
