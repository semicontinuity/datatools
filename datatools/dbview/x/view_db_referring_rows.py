import sys
from typing import Optional

from picotui.defs import KEY_ENTER

from datatools.dbview.util.pg import get_table_foreign_keys_inbound_from, execute_sql
from datatools.dbview.x.types import View, EntityReference, DbReferringRows, DbRowReference, DbTableRowsSelector, \
    DbSelectorClause
from datatools.dbview.x.util.pg import connect_to_db
from datatools.json.util import to_jsonisable
from datatools.jv.app import loop, make_document
from datatools.jv.document import JDocument
from datatools.tui.screen_helper import with_alternate_screen
from datatools.util.logging import debug


class ViewDbReferringRows(View):

    def __init__(self, e_ref: DbReferringRows) -> None:
        self.e_ref = e_ref

    def run(self) -> Optional[EntityReference]:
        with connect_to_db() as conn:
            # Fetch relation, because in e_ref there is no information, to which column we refer.
            relations = get_table_foreign_keys_inbound_from(conn, self.e_ref.source.table, self.e_ref.target.table)
            if len(relations) != 1:
                raise Exception()

            source_table = relations[0]['table_name']
            source_column = relations[0]['column_name']
            target_table = relations[0]['foreign_table_name']
            target_column = relations[0]['foreign_column_name']

            if target_column != self.e_ref.target.where[0].column:
                sql = f"SELECT * from {source_table} where {source_column}=(select {target_column} from {target_table} where {self.e_ref.target.where[0].column} {self.e_ref.target.where[0].op} {self.e_ref.target.where[0].value}) limit 2"
            else:
                sql = f"SELECT * from {source_table} where {source_column}={self.e_ref.target.where[0].value} limit 2"
            rows = to_jsonisable(execute_sql(conn, sql))
            doc: JDocument = make_document(rows)
            key_code, cur_line = with_alternate_screen(lambda: loop(doc))
            return self.handle_loop_result(doc, key_code, cur_line)

    def handle_loop_result(self, document, key_code, cur_line: int) -> Optional[EntityReference]:
        if key_code == KEY_ENTER:
            path = document.selected_path(cur_line)
            if len(path) == 2:
                value = document.selected_value(cur_line)
                reference = DbRowReference(selector=DbTableRowsSelector(table=self.e_ref.source.table, where=[
                    DbSelectorClause(path[1], '=', f"'{value}'")]))
                return reference
