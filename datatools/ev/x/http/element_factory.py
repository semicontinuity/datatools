from typing import Optional, Hashable, Any

from picotui.defs import KEY_ENTER

from datatools.ev.x.http.types import RestEntity
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.JString import JString
from datatools.jv.model.JValueElement import JValueElement
from datatools.jv.model.j_element_factory import JElementFactory
from datatools.tui.buffer.abstract_buffer_writer import AbstractBufferWriter
from datatools.tui.treeview.rich_text import Style


class MyElementFactory(JElementFactory):
    concepts: 'RealmRest'
    entity: RestEntity
    value: Any

    def __init__(self, concepts: 'RealmRest', entity: RestEntity):
        super().__init__(None)
        self.concepts = concepts
        self.entity = entity

    def build_root_model(self, v, k: Optional[Hashable] = None) -> JValueElement:
        self.value = v
        return super().build_root_model(v, k)

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
        """
        Invoked for every created element that is a link
        """
        link_spec = self.concepts.find_link_spec(self.entity.concept, '.'.join([str(p) for p in parent.path()] + [str(k)]))
        if link_spec:
            concept, var, values = link_spec
            path_variables = self.concepts.get_path_variables(concept)

            vars = {k: v for k, v in self.entity.variables.items()
                    if k in path_variables}\
                   | {var: str(v)}
            if values:
                vars |= self._values(values)

            target = RestEntity(realm_name=None, concept=concept, variables=vars)
            return link_element_f(v, k).set_entity(target)
        else:
            return plain_element_f(v, k)

    def _values(self, values):
        """
        Handle "values" element of the concept link spec.
        Format: "values": [ { "value": "var_name", "key": "key of field in document (only top-level)" }, ... ]
        """
        return {val["value"]: str(self.value[val["key"]]) for val in values}
