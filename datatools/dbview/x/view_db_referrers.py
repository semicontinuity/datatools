from collections import defaultdict
from typing import Optional, List

from datatools.dbview.util.pg import get_table_foreign_keys_inbound
from datatools.dbview.x.types import DbRowReference, View, EntityReference, DbReferrers, DbSelectorClause
from datatools.dbview.x.util.pg import connect_to_db
from datatools.jv.app import loop, make_document
from datatools.tui.screen_helper import with_alternate_screen


class ViewDbReferrers(View):

    def __init__(self, e_ref: DbReferrers) -> None:
        self.e_ref = e_ref

    def run(self) -> Optional[EntityReference]:
        with connect_to_db() as conn:
            inbound_relations = get_table_foreign_keys_inbound(conn, self.e_ref.table)
            tree = self.make_referring_rows_model(inbound_relations)
            doc = make_document(tree)
            key_code, cur_line = with_alternate_screen(lambda: loop(doc))
            return self.handle_loop_result(doc, key_code, cur_line)

    def make_referring_rows_model(conn, inbound_relations):
        result = defaultdict(list)

        for inbound_relation in inbound_relations:
            result[inbound_relation['table_name']].append(inbound_relation['column_name'])

        return result

    def handle_loop_result(self, document, key_code, cur_line: int) -> DbRowReference:
        pass
