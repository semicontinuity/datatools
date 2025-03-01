import os.path
from os.path import relpath

import psycopg2

from datatools.util.logging import debug


class PgDataSource:

    def __init__(self, props):
        self.props = props

    def connect_to_db(self):
        debug('Connecting')
        c = psycopg2.connect(
            host=self.get_host(),
            port=self.get_port(),
            dbname=self.get_env('DB_NAME'),
            user=self.get_env('DB_USER'),
            password=self.get_env('PASSWORD'),
            # sslmode="verify-ca",
            # sslmode="verify-full",
            target_session_attrs="read-write"
        )
        debug('Connected')
        return c

    def get_host(self):
        if self.props.get('LOCAL_PORT'):
            # tunnel
            return 'localhost'
        return self.get_env('HOST')

    def get_port(self):
        if self.props.get('LOCAL_PORT'):
            # tunnel
            return self.get_env('LOCAL_PORT')
        return self.get_env('PORT')

    def get_realm_ctx(self):
        return relpath(os.path.abspath(self.get_env('CTX_BASE') + '/..'), self.get_env('CTX_DIR'))

    def get_env(self, key):
        value = self.props.get(key)
        if value is None:
            raise Exception(f'Must set {key}')
        return value
