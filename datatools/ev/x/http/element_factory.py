from typing import Optional

from picotui.defs import KEY_ENTER

from datatools.ev.x.http.concepts import Concepts
from datatools.ev.x.http.types import RestEntity
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.factory import JElementFactory
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.treeview.rich_text import Style


class MyElementFactory(JElementFactory):
    concepts: Concepts
    concept: str

    def __init__(self, concepts: Concepts, concept: str):
        super().__init__(None)
        self.concepts = concepts
        self.concept = concept

    class JMyNumber(JNumber):
        concept: str

        def set_concept(self, concept: str):
            self.concept = concept
            return self

        def value_style(self):
            return Style(AbstractBufferWriter.MASK_ITALIC | AbstractBufferWriter.MASK_UNDERLINED, (192, 96, 96))

        def handle_key(self, key: str):
            if key == KEY_ENTER:
                return RestEntity(self.concept, self.value)

    def make_number_element(self, v, k, parent: Optional[JElement] = None):
        concept = self.concepts.find_link_concept(self.concept, parent.path() + [k])
        if concept:
            return MyElementFactory.JMyNumber(v, k).set_concept(concept)
        else:
            return JNumber(v, k)
