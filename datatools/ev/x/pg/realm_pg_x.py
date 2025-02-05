from typing import Dict

from datatools.ev.x.pg.realm_pg import RealmPg
import os
import json


class PgPropertySource:

    def __init__(self, props):
        self.props = props

    def realm_pg(self, name: str, links: Dict[str, Dict]) -> RealmPg:
        return RealmPg(
            name,
            self.get_host(),
            self.get_port(),
            self.get_env('DB_NAME'),
            self.get_env('DB_USER'),
            self.get_env('PASSWORD'),
            links
        )

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

    def get_env(self, key):
        value = self.props.get(key)
        if value is None:
            raise Exception(f'Must set {key}')
        return value
