from typing import Optional

from datatools.ev.x.concepts import Concepts
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.factory import JElementFactory
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.treeview.rich_text import Style


class MyElementFactory(JElementFactory):
    concepts: Concepts

    def __init__(self, concepts: Concepts):
        super().__init__(None)
        self.concepts = concepts

    class JMyNumber(JNumber):
        def value_style(self):
            return Style(AbstractBufferWriter.MASK_ITALIC | AbstractBufferWriter.MASK_UNDERLINED, (192, 96, 96))

    def make_number_element(self, v, k, parent: Optional[JElement] = None):
        concept = self.concepts.find_concept(parent.path() + [k])
        if concept:
            return MyElementFactory.JMyNumber(v, k)
        else:
            return JNumber(v, k)
