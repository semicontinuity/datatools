from typing import Dict

import clickhouse_connect
from clickhouse_connect.driver import Client

from datatools.ev.app_types import Realm, EntityReference, View
from datatools.ev.x.ch.clickhouse_connection_settings import ClickhouseConnectionSettings
from datatools.ev.x.ch.types import ClickhouseRowEntity
from datatools.ev.x.ch.view_ch_row import ViewChRow
from datatools.json.util import to_jsonisable


class RealmClickhouse(Realm):
    connection_settings: ClickhouseConnectionSettings
    links: Dict[str, Dict]

    def __init__(
            self,
            name: str,
            connection_settings: ClickhouseConnectionSettings,
            links: Dict[str, Dict],
    ):
        super().__init__(name)
        self.connection_settings = connection_settings
        self.links = links

    # override
    def create_view(self, e_ref: EntityReference) -> View:
        if isinstance(e_ref, ClickhouseRowEntity):
            return ViewChRow(self, e_ref.selector)

    def connect_to_db(self) -> Client:
        return clickhouse_connect.get_client(
            host=self.connection_settings.hostname,
            port=self.connection_settings.port,
            secure=self.connection_settings.secure,
            verify=False,
            username=self.connection_settings.user,
            password=self.connection_settings.password,
            database=self.connection_settings.database,
        )

    def execute_sql_query(self, conn: Client, sql_query: str):
        result = conn.query(sql_query)
        return [
            {column_name: to_jsonisable(row[i]) for i, column_name in enumerate(result.column_names)}
            for row in result.result_rows
        ]
