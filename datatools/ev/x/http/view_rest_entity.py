from typing import Optional

from datatools.ev.app_types import View, EntityReference
from datatools.ev.x.http.element_factory import MyElementFactory
from datatools.ev.x.http.rest_entity_grid import RestEntityGrid
from datatools.ev.x.http.types import RestEntity
from datatools.jv.app import do_loop, make_document_for_model, make_tree_grid
from datatools.jv.jdocument import JDocument
from datatools.jv.jgrid import JGrid
from datatools.tui.screen_helper import with_alternate_screen
from datatools.tui.terminal import screen_size_or_default


class ViewRestEntity(View):
    ref: RestEntity
    doc: JDocument

    def __init__(self, ref: RestEntity, concepts: 'RealmRest') -> None:
        self.ref = ref
        self.concepts = concepts

    def build(self):
        j = self.concepts.fetch_json(self.ref)
        self.doc = make_document_for_model(
            MyElementFactory(self.concepts, self.ref).build_root_model(j),
            j,
            footer=f'{self.ref.concept} {self.ref.variables}'
        )
        self.g = with_alternate_screen(lambda: make_tree_grid(self.doc, screen_size_or_default(), RestEntityGrid))

    def run(self) -> Optional[EntityReference]:
        key_code, cur_line = with_alternate_screen(lambda: do_loop(self.g))
        return self.handle_loop_result(self.doc, key_code, cur_line)

    def handle_loop_result(self, document, key_code, cur_line: int) -> Optional[EntityReference]:
        return key_code
