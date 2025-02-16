from typing import List, Optional, Dict

from picotui.defs import KEY_ENTER

from datatools.dbview.util.pg import get_table_pks
from datatools.ev.app_types import View, EntityReference
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause, DbRowReference
from datatools.ev.x.pg.view_db_rows_grid import ViewDbRowsGrid
from datatools.jt.app.app_kit import load_data_bundle, CmdLineParams
from datatools.jt.app.ng.grid_factory import grid
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default


class ViewDbRows(View):
    realm: 'RealmPg'
    selector: DbTableRowsSelector
    rows: List[Dict]
    g: ViewDbRowsGrid

    def __init__(self, realm: 'RealmPg', selector: DbTableRowsSelector) -> None:
        self.realm = realm
        self.selector = selector

    # @override
    def build(self):
        with self.realm.connect_to_db() as conn:
            self.table_pks = get_table_pks(conn, self.selector.table)
            self.rows = self.get_entity_rows(conn, self.selector.table, self.selector.where)
            self.table_pks = get_table_pks(conn, self.selector.table)

        self.g = with_alternate_screen(
            lambda: grid(
                ViewDbRowsGrid,
                screen_size_or_default(),
                load_data_bundle(
                    CmdLineParams(),
                    self.rows,
                )
            )
        )

    # @override
    def run(self) -> Optional[EntityReference]:
        loop_result, cur_line = with_alternate_screen(lambda: self.do_loop(self.g))
        if loop_result == KEY_ENTER:
            sel_entity = self.rows[cur_line]
            return DbRowReference(
                realm_name=self.realm.name,
                selector=DbTableRowsSelector(
                    table=self.selector.table,
                    where=[DbSelectorClause(pk, '=', "'" + sel_entity[pk] + "'") for pk in self.table_pks]
                )
            )

    def get_entity_rows(self, conn, table: str, where: List[DbSelectorClause]):
        where_string = self.make_where_string(where)
        sql = f"SELECT * from {table}"
        if where_string:
            sql += f" where {where_string}"
        return self.realm.execute_query(conn, sql)

    @staticmethod
    def make_where_string(clauses: List[DbSelectorClause]):
        return '\n and \n'.join(f'{c.column} {c.op} {c.value}' for c in clauses)

    def do_loop(self, g):
        loop_result = g.loop()
        cur_line = g.cur_line
        return loop_result, cur_line
