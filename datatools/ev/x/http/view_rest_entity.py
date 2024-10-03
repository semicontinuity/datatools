from typing import Optional

from datatools.dbview.share.app_types import View, EntityReference
from datatools.ev.x.http.concepts import Concepts
from datatools.ev.x.http.element_factory import MyElementFactory
from datatools.ev.x.http.types import RestEntity
from datatools.jv.app import make_grid, do_loop, make_document_for_model
from datatools.jv.document import JDocument
from datatools.tui.screen_helper import with_alternate_screen


class ViewRestEntity(View):
    ref: RestEntity
    doc: JDocument

    def __init__(self, ref: RestEntity, concepts: Concepts) -> None:
        self.ref = ref
        self.concepts = concepts

    def build(self):
        j = self.concepts.fetch_json(self.ref)
        self.doc = make_document_for_model(
            MyElementFactory(self.concepts, self.ref).build_root_model(j),
            f'{self.ref.concept} {self.ref.variables}'
        )
        self.g = with_alternate_screen(lambda: make_grid(self.doc))

    def run(self) -> Optional[EntityReference]:
        key_code, cur_line = with_alternate_screen(lambda: do_loop(self.g))
        return self.handle_loop_result(self.doc, key_code, cur_line)

    def handle_loop_result(self, document, key_code, cur_line: int) -> Optional[EntityReference]:
        return key_code
