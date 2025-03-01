from typing import Optional

from datatools.dbview.x.util.db_query import DbQueryFilterClause
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
    def build_for_db_entity_data(self, db_entity_data: DbEntityData):
        self.db_entity_data = db_entity_data

        bundle = load_data_bundle(
            CmdLineParams(),
            self.db_entity_data.rows,
        )
        self.g: ViewDbRowsGrid = do_make_grid(bundle, ViewDbRowsGrid)
        self.g.db_entity_data = self.db_entity_data
        init_grid(
            self.g,
            with_alternate_screen(lambda: screen_size_or_default()),
            bundle
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

    def do_loop(self, g):
        loop_result = g.loop()
        cur_line = g.cur_line
        return loop_result, cur_line
