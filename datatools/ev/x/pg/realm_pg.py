from typing import Dict, Any

import psycopg2

from datatools.dbview.util.pg import get_table_foreign_keys_outbound


class RealmPg:
    host: str
    port: str
    db_name: str
    db_user: str
    db_password: str

    def __init__(self, host: str, port: str, db_name: str, db_user: str, db_password: str) -> None:
        self.host = host
        self.port = port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password

    def connect_to_db(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            sslmode="verify-full",
            target_session_attrs="read-write"
        )


def make_references(conn, table) -> Dict[str, Any]:
    """ Returns dict: column_name -> { foreign table name + foreign table column } """
    outbound_relations = get_table_foreign_keys_outbound(conn, table)
    return {
        entry['column_name']: {
            'concept': entry['foreign_table_name'],
            'concept-pk': entry['foreign_column_name'],
        }
        for entry in outbound_relations
    }
