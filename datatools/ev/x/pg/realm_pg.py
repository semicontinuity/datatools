from typing import Dict, Any
from typing import Tuple, List

from datatools.dbview.util.pg import execute_sql, describe_table, get_table_pks
from datatools.dbview.util.pg import get_table_foreign_keys_outbound
from datatools.dbview.x.util.db_query import DbQuery
from datatools.dbview.x.util.pg_query import query_to_string
from datatools.ev.app_types import EntityReference, View, Realm
from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.types import DbRowReference, DbRowsReference, DbReferrers
from datatools.ev.x.pg.view_db_referrers import ViewDbReferrers
from datatools.ev.x.pg.view_db_row import ViewDbRow
from datatools.ev.x.pg.view_db_rows import ViewDbRows
from datatools.json.util import to_jsonisable
from datatools.util.logging import debug


class RealmPg(Realm):
    data_source: PgDataSource
    links: Dict[str, Dict]

    def __init__(self, name: str, data_source: PgDataSource, links: Dict[str, Dict]):
        super().__init__(name)
        self.data_source = data_source
        self.links = links

    def connect_to_db(self):
        return self.data_source.connect_to_db()

    def find_link_spec(self, concept: str, json_path: str):
        concept_def = self.links[concept]
        for link in concept_def['links']:
            match = json_path == link['json_path']
            if match is not None:
                return link['concept'], link['value']

    # override
    def create_view(self, e_ref: EntityReference) -> View:
        debug('create_view', e_ref=e_ref)
        if isinstance(e_ref, DbRowsReference):
            return ViewDbRows(self, e_ref.query)
        elif isinstance(e_ref, DbRowReference):
            return ViewDbRow(self, e_ref.selector, e_ref.query)
        elif isinstance(e_ref, DbReferrers):
            return ViewDbReferrers(self, e_ref.selector)

    def get_selector_value(self, conn, inbound_relation, table, where):
        this_column = inbound_relation['foreign_column_name']
        where_column, where_op, where_value = where[0].column, where[0].op, where[0].value
        if where_op != '=':
            raise Exception('WHERE clause must be PK equality')
        if this_column != where_column:
            sql = f"SELECT {this_column} from {table} where {where_column} {where_op} {where_value}"
            debug(sql)
            rows = self.execute_sql_query(conn, sql)
            if len(rows) != 1:
                raise Exception(f'illegal state: expected 1 row, but was {len(rows)}')
            selector_value = "'" + rows[0][this_column] + "'"
        else:
            selector_value = where_value
        return selector_value

    def get_pk_and_text_values_for_selected_rows(
            self, conn, table: str, selector_column_name: str, selector_column_value: str, table_pks: List, limit: int = 20
    ) -> Tuple[List, List]:
        d = describe_table(conn, table)
        text_columns = [row['column_name'] for row in d if row['data_type'] == 'text']

        columns = table_pks + text_columns

        sql = f"SELECT {', '.join(columns)} from {table} where {selector_column_name}={selector_column_value} limit {limit}"
        debug(sql)
        rows = self.execute_sql_query(conn, sql)
        return [{k: to_jsonisable(v) for k, v in row.items() if k in table_pks} for row in rows], [
            {k: to_jsonisable(v) for k, v in row.items() if k not in table_pks} for row in rows]

    def make_references(self, conn, table) -> Dict[str, Any]:
        """ Returns dict: column_name -> { "concept":"...", "concept-pk":"..." } """
        outbound_relations = get_table_foreign_keys_outbound(conn, table)
        return {
            entry['column_name']: {
                'concept': entry['foreign_table_name'],
                'concept-pk': entry['foreign_column_name'],
            }
            for entry in outbound_relations
        }

    def execute_sql_query(self, conn, sql: str) -> list[dict[str, Any]]:
        return execute_sql(conn, sql)

    def db_entity_data(self, conn, query: DbQuery) -> DbEntityData:
        return DbEntityData(
            rows=execute_sql(conn, query_to_string(query)),
            pks=get_table_pks(conn, query.table),
        )
