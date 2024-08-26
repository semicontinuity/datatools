from collections import defaultdict
from typing import Optional

from picotui.defs import KEY_ENTER

from datatools.dbview.util.pg import get_table_foreign_keys_inbound
from datatools.dbview.x.types import View, EntityReference, DbTableRowsSelector, DbReferringRows, \
    DbTableColumn
from datatools.dbview.x.util.pg import connect_to_db
from datatools.jv.app import loop, make_document
from datatools.tui.screen_helper import with_alternate_screen


class ViewDbReferrers(View):

    def __init__(self, e_ref: DbTableRowsSelector) -> None:
        self.selector = e_ref

    def run(self) -> Optional[EntityReference]:
        with connect_to_db() as conn:
            inbound_relations = get_table_foreign_keys_inbound(conn, self.selector.table)
            tree = self.make_referring_rows_model(inbound_relations)
            doc = make_document(tree)
            key_code, cur_line = with_alternate_screen(lambda: loop(doc))
            return self.handle_loop_result(doc, key_code, cur_line)

    def make_referring_rows_model(conn, inbound_relations):
        result = defaultdict(dict)

        for inbound_relation in inbound_relations:
            result[inbound_relation['table_name']][inbound_relation['column_name']] = inbound_relation['foreign_column_name']

        return result

    def handle_loop_result(self, document, key_code, cur_line: int) -> Optional[DbReferringRows]:
        if key_code == KEY_ENTER:
            path = document.selected_path(cur_line)
            value = document.selected_value(cur_line)
            if len(path) == 2:
                return DbReferringRows(
                    source=DbTableColumn(table=path[0], column=path[0]),
                    target=self.selector
                )
