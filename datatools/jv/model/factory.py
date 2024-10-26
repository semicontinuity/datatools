import os
from collections import defaultdict
from typing import List, Optional, Hashable

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
            json = 'YAML' not in os.environ
            options = JViewOptions(
                quotes=json,
                commas=json,
            )
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
        model = self.build_model_raw(v, k, parent)
        model.parent = parent
        return model

    def build_model_raw(self, v, k: Optional[Hashable], parent: Optional[JElement] = None) -> JValueElement:
        if v is None:
            return self.null(k)
        elif type(v) is str:
            return self.string(v, k, parent)
        elif type(v) is int or type(v) is float:
            return self.number(v, k, parent)
        elif type(v) is bool:
            return self.boolean(v, k, parent)
        elif type(v) is dict or type(v) is defaultdict:
            return self.object(v, k, parent)
        elif type(v) is list:
            return self.array(v, k, parent)
        else:
            v.set_key(k)
            return v

    def boolean(self, v, k, parent: Optional[JElement] = None):
        e = JBoolean(v, k)
        e.parent = parent
        e.options = self.options
        return e

    def number(self, v, k, parent: Optional[JElement] = None):
        e = self.make_number_element(v, k, parent)
        e.parent = parent
        e.options = self.options
        return e

    def make_number_element(self, v, k, parent: Optional[JElement] = None):
        return JNumber(v, k)

    def string(self, v, k, parent: Optional[JElement] = None):
        e = self.make_string_element(k, v, parent)
        e.parent = parent
        e.options = self.options
        return e

    def make_string_element(self, k, v, parent: Optional[JElement] = None):
        return JString(v, k)

    def null(self, k, parent: Optional[JElement] = None) -> JNull:
        e = JNull(None, k)
        e.options = self.options
        e.parent = parent
        return e

    def array(self, v, k, parent: Optional[JElement] = None):
        e = JArray(v, k)
        e.options = self.options
        e.parent = parent
        e.set_elements(set_last_in_parent([self.build_model(v, i, e) for i, v in enumerate(v)]))
        return e

    def object(self, v, k, parent: Optional[JElement] = None):
        e = JObject(v, k)
        e.parent = parent
        e.options = self.options
        e.set_elements(set_last_in_parent(set_padding([self.build_model(v, k1, e) for k1, v in v.items()])))
        return e
