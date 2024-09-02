from collections import defaultdict
from typing import List, Optional, Dict, Hashable

from datatools.jv.model import JObject, JArray
from datatools.jv.model.JArray import JArray
from datatools.jv.model.JBoolean import JBoolean
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JNull import JNull
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JString import JString
from datatools.jv.model.JValueElement import JValueElement
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement
from datatools.jv.model.JComplexElement import JComplexElement


def set_padding(elements: List[JValueElement]) -> List[JValueElement]:
    max_field_name_length = 0 if len(elements) == 0 else max(len(e.key) for e in elements)
    for e in elements:
        e.padding = max_field_name_length - len(e.key) + 1
    return elements


class JElementFactory:
    INDENT = 2

    def build_root_model(self, v, k: Optional[Hashable] = None, last_in_parent=True) -> JValueElement:
        model = self.build_model(v, k, last_in_parent)
        self.set_indent_recursive(model, 0)
        return model

    def build_model(self, v, k: Optional[Hashable] = None, last_in_parent=True, parent: Optional[JElement] = None) -> JValueElement:
        model = self.build_model_raw(v, k, last_in_parent)
        model.parent = parent
        return model

    def build_model_raw(self, v, k: Optional[str], last_in_parent=True) -> JValueElement:
        if v is None:
            return JNull(None, k, last_in_parent)
        elif type(v) is str:
            return JString(v, k, last_in_parent)
        elif type(v) is int or type(v) is float:
            return JNumber(v, k, last_in_parent)
        elif type(v) is bool:
            return JBoolean(v, k, last_in_parent)
        elif type(v) is dict or type(v) is defaultdict:
            return JObject(v, k, set_padding(self.build_object_fields_models(v)), last_in_parent)
        elif type(v) is list:
            return JArray(v, k, self.build_array_items_models(v), last_in_parent)
        else:
            v.set_key(k)
            return v

    def build_object_fields_models(self, v) -> List[JValueElement]:
        fields = []
        i = 0
        size = len(v)
        for k, v in v.items():
            model = self.build_model(v, k, i >= size - 1)
            fields.append(model)
            i += 1
        return fields

    def build_array_items_models(self, v) -> List[JValueElement]:
        items = []
        size = len(v)
        for i, v in enumerate(v):
            items.append(self.build_model(v, i, i >= size - 1))
            i += 1
        return items

    def set_indent_recursive(self, model: JElement, indent: int):
        model.indent = indent
        if issubclass(type(model), JComplexElement):
            model.start.indent = indent
            model.end.indent = indent
            for e in model.elements:
                self.set_indent_recursive(e, indent + self.INDENT)
