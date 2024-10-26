from typing import List, Optional

from datatools.dbview.util.pg import get_table_pks
from datatools.ev.app_types import View, EntityReference
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause
from datatools.jt.app.app_kit import load_data_bundle, CmdLineParams
from datatools.jt.app.ng.main import grid
from datatools.jt.model.data_bundle import DataBundle
from datatools.jt.model.metadata import Metadata
from datatools.jt.model.presentation import Presentation
from datatools.jt.model.values_info import ColumnsValuesInfo
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default


class ViewDbRows(View):
    realm: 'RealmPg'
    selector: DbTableRowsSelector

    def __init__(self, realm: 'RealmPg', selector: DbTableRowsSelector) -> None:
        self.realm = realm
        self.selector = selector

    # @override
    def build(self):
        with self.realm.connect_to_db() as conn:
            self.table_pks = get_table_pks(conn, self.selector.table)
            rows = self.get_entity_rows(conn, self.selector.table, self.selector.where)

            self.g = with_alternate_screen(
                lambda: grid(
                    screen_size_or_default(),
                    load_data_bundle(
                        CmdLineParams(),
                        rows,
                    )
                )
            )

    def run(self) -> Optional[EntityReference]:
        loop_result, cur_line = with_alternate_screen(lambda: self.do_loop(self.g))

    def get_entity_rows(self, conn, table: str, where: List[DbSelectorClause]):
        where_string = self.make_where_string(where)
        sql = f"SELECT * from {table} where {where_string}"
        return self.realm.execute_query(conn, sql)

    @staticmethod
    def make_where_string(clauses: List[DbSelectorClause]):
        return '\n and \n'.join(f'{c.column} {c.op} {c.value}' for c in clauses)

    def do_loop(self, g):
        loop_result = g.loop()
        cur_line = g.cur_line
        return loop_result, cur_line
