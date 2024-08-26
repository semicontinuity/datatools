from typing import Optional

from datatools.dbview.x.types import DbRowReference, View, EntityReference, DbReferrers
from datatools.jv.app import loop, make_document
from datatools.tui.screen_helper import with_alternate_screen


class ViewDbReferrers(View):

    def __init__(self, e_ref: DbReferrers) -> None:
        self.e_ref = e_ref

    def run(self) -> Optional[EntityReference]:
        tree = {'a': 'A'}
        doc = make_document(tree)
        key_code, cur_line = with_alternate_screen(lambda: loop(doc))
        return self.handle_loop_result(doc, key_code, cur_line)

    def handle_loop_result(self, document, key_code, cur_line: int) -> DbRowReference:
        pass
