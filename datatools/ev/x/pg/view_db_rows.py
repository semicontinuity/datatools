from typing import List, Optional

from datatools.dbview.x.util.db_query import DbQueryFilterClause
from datatools.dbview.x.util.pg_query import query_to_string
from datatools.ev.app_types import EntityReference
from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.ev.x.pg.types import DbTableRowsSelector, DbSelectorClause, DbRowReference
from datatools.ev.x.pg.view_db import ViewDb
from datatools.ev.x.pg.view_db_rows_grid import ViewDbRowsGrid
from datatools.jt.app.app_kit import load_data_bundle, CmdLineParams
from datatools.jt.app.ng.jt_ng_grid_factory import init_grid, do_make_grid
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default
from picotui.defs import KEY_ENTER


class ViewDbRows(ViewDb):
    db_entity_data: DbEntityData
    g: ViewDbRowsGrid

    # @override
    def build(self):
        sql = query_to_string(self.query)

        with self.realm.connect_to_db() as conn:
            self.db_entity_data = self.realm.db_entity_data(conn, self.query)

        bundle = load_data_bundle(
            CmdLineParams(),
            self.db_entity_data.rows,
        )

        grid: ViewDbRowsGrid = do_make_grid(bundle, ViewDbRowsGrid)
        grid.query = self.query
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
            sel_entity = self.db_entity_data.rows[cur_line]
            return DbRowReference(
                realm_name=self.realm.name,
                selector=DbTableRowsSelector(
                    table=self.query.table,
                    where=[DbSelectorClause(pk, '=', "'" + str(sel_entity[pk]) + "'") for pk in self.db_entity_data.pks]
                ),
                query=self.query.with_filter_clauses([DbQueryFilterClause(pk, '=', sel_entity[pk]) for pk in self.db_entity_data.pks])
            )
        else:
            raise Exception(loop_result)

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
