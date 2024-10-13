from typing import Optional

from picotui.defs import KEY_ENTER

from datatools.ev.x.http.concepts import Concepts
from datatools.ev.x.http.types import RestEntity
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.JString import JString
from datatools.jv.model.factory import JElementFactory
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.treeview.rich_text import Style


class MyElementFactory(JElementFactory):
    concepts: Concepts
    entity: RestEntity

    def __init__(self, concepts: Concepts, entity: RestEntity):
        super().__init__(None)
        self.concepts = concepts
        self.entity = entity

    class JMyNumber(JNumber):
        entity: RestEntity

        def set_entity(self, entity: RestEntity):
            self.entity = entity
            return self

        def value_style(self) -> Style:
            return super().value_style().with_attr(AbstractBufferWriter.MASK_ITALIC | AbstractBufferWriter.MASK_UNDERLINED)

        def handle_key(self, key: str):
            if key == KEY_ENTER:
                return self.entity

    class JMyString(JString):
        entity: RestEntity

        def set_entity(self, entity: RestEntity):
            self.entity = entity
            return self

        def value_style(self) -> Style:
            return super().value_style().with_attr(AbstractBufferWriter.MASK_ITALIC | AbstractBufferWriter.MASK_UNDERLINED)

        def handle_key(self, key: str):
            if key == KEY_ENTER:
                return self.entity

    # override
    def make_number_element(self, v, k, parent: Optional[JElement] = None):
        return self._make_element(k, v, parent, MyElementFactory.JMyNumber, JNumber)

    # override
    def make_string_element(self, k, v, parent: Optional[JElement] = None):
        return self._make_element(k, v, parent, MyElementFactory.JMyString, JString)

    def _make_element(self, k, v, parent: Optional[JElement], link_element_f, plain_element_f):
        link_spec = self.concepts.find_link_spec(self.entity.concept, '.'.join([str(p) for p in parent.path()] + [str(k)]))
        if link_spec:
            concept, var = link_spec
            vars = { k: v for k, v in self.entity.variables.items() if k in self.concepts.get_path_variables(concept)} | {var: str(v)}
            target = RestEntity(realm_name=None, concept=concept, variables=vars)
            return link_element_f(v, k).set_entity(target)
        else:
            return plain_element_f(v, k)
