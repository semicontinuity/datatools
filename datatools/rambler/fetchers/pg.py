def fetch(query, variables):
    """
    query format:
    List of {"table":"...", "column":"..."}
    """
    host = get_var(variables, 'HOST')
    port = get_var(variables, 'PORT')
    db_name = get_var(variables, 'DB_NAME')
    db_user = get_var(variables, 'DB_USER')
    password = get_var(variables, 'PASSWORD')

    tables = {}

    sql_lines = []
    sql_lines.append('select')
    sql_lines.append(',\n'.join([f'  __t{tables[query_item["table"]]}.{query_item["column"]}' for query_item in query]))
    sql_lines.append('from')
    sql_lines.append(','.join([f'{name} as __t{i}' for i, name in enumerate(tables)]))

    return '\n'.join(sql_lines)


def get_var(variables, key):
    value = variables.get(key)
    if value is None:
        raise Exception(f'Must set {key}')
    return value
