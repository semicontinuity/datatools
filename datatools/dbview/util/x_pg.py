import os

import psycopg2


def connect_to_db():
    host = get_env('HOST')
    port = get_env('PORT')
    db_name = get_env('DB_NAME')
    db_user = get_env('DB_USER')
    password = get_env('PASSWORD')
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=db_name,
        user=db_user,
        password=password,
        sslmode="verify-full",
        target_session_attrs="read-write"
    )


def get_env(key):
    value = os.getenv(key)
    if value is None:
        raise Exception(f'Must set {key}')
    return value
