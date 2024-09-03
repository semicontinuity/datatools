import os
from collections import defaultdict
from typing import List, Optional, Hashable, Dict

from datatools.jv.model import JObject, JArray, JViewOptions
from datatools.jv.model.JArray import JArray
from datatools.jv.model.JBoolean import JBoolean
from datatools.jv.model.JComplexElement import JComplexElement
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JNull import JNull
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JString import JString
from datatools.jv.model.JValueElement import JValueElement


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


class JElementFactory:
    options: JViewOptions

    def __init__(self, options: JViewOptions = None) -> None:
        if options is None:
            options = JViewOptions(quotes='YAML' not in os.environ)
            # options = JViewOptions(quotes=True)
        self.options = options

    def set_indent_recursive(self, model: JValueElement, indent: int = 0) -> JValueElement:
        model.indent = indent
        if issubclass(type(model), JComplexElement):
            model.start.indent = indent
            model.end.indent = indent
            for e in model.elements:
                self.set_indent_recursive(e, indent + self.options.indent)
        return model

    def build_root_model(self, v, k: Optional[Hashable] = None) -> JValueElement:
        return self.set_indent_recursive(self.build_model(v, k))

    def build_model(self, v, k: Optional[Hashable] = None, parent: Optional[JElement] = None) -> JValueElement:
        model = self.build_model_raw(v, k)
        model.parent = parent
        return model

    def build_model_raw(self, v, k: Optional[str]) -> JValueElement:
        if v is None:
            return self.null(k)
        elif type(v) is str:
            return self.string(v, k)
        elif type(v) is int or type(v) is float:
            return self.number(v, k)
        elif type(v) is bool:
            return self.boolean(v, k)
        elif type(v) is dict or type(v) is defaultdict:
            return self.build_object_model(v, k, self.build_object_fields_models(v))
        elif type(v) is list:
            return self.build_array_model(v, k, self.build_array_items_models(v))
        else:
            v.set_key(k)
            return v

    def boolean(self, v, k):
        e = JBoolean(v, k)
        e.options = self.options
        return e

    def number(self, v, k):
        e = JNumber(v, k)
        e.options = self.options
        return e

    def string(self, v, k):
        e = JString(v, k)
        e.options = self.options
        return e

    def null(self, k) -> JNull:
        e = JNull(None, k)
        e.options = self.options
        return e

    def build_array_model(self, v, k, items_models):
        e = JArray(v, k, set_last_in_parent(items_models))
        e.options = self.options
        return e

    def build_object_model(self, v, k, element_models):
        e = JObject(v, k, set_last_in_parent(set_padding(element_models)))
        e.options = self.options
        return e

    def build_object_fields_models(self, v: Dict) -> List[JValueElement]:
        return [self.build_model(v, k) for k, v in v.items()]

    def build_array_items_models(self, v: List) -> List[JValueElement]:
        return [self.build_model(v, i) for i, v in enumerate(v)]
