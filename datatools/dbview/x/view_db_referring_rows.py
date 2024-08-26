from typing import Optional

from datatools.dbview.x.types import View, EntityReference, DbReferringRows
from datatools.dbview.x.util.pg import connect_to_db
from datatools.jv.app import loop, make_document
from datatools.tui.screen_helper import with_alternate_screen


class ViewDbReferringRows(View):

    def __init__(self, e_ref: DbReferringRows) -> None:
        self.e_ref = e_ref

    def run(self) -> Optional[EntityReference]:
        with connect_to_db() as conn:
            tree = [
                1
            ]
            doc = make_document(tree)
            key_code, cur_line = with_alternate_screen(lambda: loop(doc))
            return self.handle_loop_result(doc, key_code, cur_line)

    def handle_loop_result(self, document, key_code, cur_line: int) -> Optional[DbReferringRows]:
        pass