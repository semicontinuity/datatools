from typing import List, Optional, Dict

from picotui.defs import KEY_ENTER

from datatools.dbview.util.pg import get_table_pks
from datatools.dbview.x.util.db_query import DbQuery
from datatools.ev.app_types import View, EntityReference
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause, DbRowReference
from datatools.ev.x.pg.view_db_rows_grid import ViewDbRowsGrid
from datatools.jt.app.app_kit import load_data_bundle, CmdLineParams
from datatools.jt.app.ng.jt_ng_grid_factory import init_grid, do_make_grid
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default


class ViewDbRows(View):
    realm: 'RealmPg'
    selector: DbTableRowsSelector
    query: DbQuery
    rows: List[Dict]
    g: ViewDbRowsGrid

    def __init__(self, realm: 'RealmPg', selector: DbTableRowsSelector, query: DbQuery = None) -> None:
        self.realm = realm
        self.selector = selector
        self.query = query

    # @override
    def build(self):
        sql = self.select_sql(self.selector.table, self.selector.where)

        with self.realm.connect_to_db() as conn:
            self.table_pks = get_table_pks(conn, self.selector.table)
            self.rows = self.realm.execute_query(conn, sql)

        bundle = load_data_bundle(
            CmdLineParams(),
            self.rows,
        )

        grid: ViewDbRowsGrid = do_make_grid(bundle, ViewDbRowsGrid)
        grid.sql = sql

        self.g = with_alternate_screen(
            lambda: init_grid(
                grid,
                screen_size_or_default(),
                bundle
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

    def select_sql(self, table, where):
        where_string = self.make_where_string(where)
        sql = f"SELECT * from {table}"
        if where_string:
            sql += f" where {where_string}"
        return sql

    @staticmethod
    def make_where_string(clauses: List[DbSelectorClause]):
        return '\n and \n'.join(f'{c.column} {c.op} {c.value}' for c in clauses)

    def do_loop(self, g):
        loop_result = g.loop()
        cur_line = g.cur_line
        return loop_result, cur_line
