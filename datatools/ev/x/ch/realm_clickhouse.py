from typing import Dict

import clickhouse_connect
from clickhouse_connect.driver import Client

from datatools.ev.app_types import Realm, EntityReference, View
from datatools.ev.x.ch.types import ClickhouseRowEntity
from datatools.ev.x.ch.view_ch_row import ViewChRow


class RealmClickhouse(Realm):
    hostname: str
    database: str
    user: str
    password: str
    links: Dict[str, Dict]

    def __init__(
            self,
            name: str,
            hostname: str,
            database: str,
            user: str,
            password: str,
            links: Dict[str, Dict],
    ):
        super().__init__(name)
        self.hostname = hostname
        self.database = database
        self.user = user
        self.password = password
        self.links = links

    # override
    def create_view(self, e_ref: EntityReference) -> View:
        if isinstance(e_ref, ClickhouseRowEntity):
            return ViewChRow(self, e_ref.selector)

    def connect_to_db(self) -> Client:
        return clickhouse_connect.get_client(
            host=self.hostname,
            port=8443,
            secure=True,
            verify=False,
            username=self.user,
            password=self.password,
            database=self.database,
        )

    def execute_query(self, conn: Client, query: str):
        result = conn.query(query)
        return [
            {column_name: row[i] for i, column_name in enumerate(result.column_names)}
            for row in result.result_rows
        ]
