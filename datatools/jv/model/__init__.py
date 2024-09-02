from collections import defaultdict
from typing import List, Optional, Hashable

from datatools.jv.model import JObject, JArray
from datatools.jv.model.JArray import JArray
from datatools.jv.model.JBoolean import JBoolean
from datatools.jv.model.JComplexElement import JComplexElement
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JNull import JNull
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement
from datatools.jv.model.JString import JString
from datatools.jv.model.JValueElement import JValueElement

INDENT = 2


def set_padding(elements: List[JValueElement]) -> List[JValueElement]:
    max_field_name_length = 0 if len(elements) == 0 else max(len(e.key) for e in elements)
    for e in elements:
        e.padding = max_field_name_length - len(e.key) + 1
    return elements


def set_last_in_parent(elements: List[JValueElement]) -> List[JValueElement]:
    if len(elements) > 0:
        for e in elements:
            e.set_last_in_parent(False)
        e.set_last_in_parent(True)
    return elements


def set_indent_recursive(model: JValueElement, indent: int = 0) -> JValueElement:
    model.indent = indent
    if issubclass(type(model), JComplexElement):
        model.start.indent = indent
        model.end.indent = indent
        for e in model.elements:
            set_indent_recursive(e, indent + INDENT)
    return model


class JElementFactory:

    def build_root_model(self, v, k: Optional[Hashable] = None, last_in_parent=True) -> JValueElement:
        return set_indent_recursive(self.build_model(v, k, last_in_parent))

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
            return self.build_object_model(v, k, self.build_object_fields_models(v))
        elif type(v) is list:
            return self.build_array_model(v, k, self.build_array_items_models(v))
        else:
            v.set_key(k)
            return v

    def build_array_model(self, v, k, items_models):
        return JArray(v, k, items_models)

    def build_object_model(self, v, k, element_models):
        return JObject(v, k, set_last_in_parent(set_padding(element_models)))

    def build_object_fields_models(self, v) -> List[JValueElement]:
        models = []
        i = 0
        model = None

        for k, v in v.items():
            model = self.build_model(v, k)
            models.append(model)
            i += 1

        if model is not None:
            model.last_in_parent = True

        return models

    def build_array_items_models(self, v) -> List[JValueElement]:
        models = []
        model = None

        for i, v in enumerate(v):
            model = self.build_model(v, i)
            models.append(model)
            i += 1

        if model is not None:
            model.last_in_parent = True

        return models
