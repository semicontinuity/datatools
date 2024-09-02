from collections import defaultdict
from typing import List, Optional

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

INDENT = 2


def build_root_model(v, k: Optional[str] = None, last_in_parent=True) -> JValueElement:
    model = build_model(v, k, last_in_parent)
    set_indent_recursive(model, 0)
    return model


def build_model(v, k: Optional[str] = None, last_in_parent=True, parent: Optional[JElement] = None) -> JValueElement:
    model = build_model_raw(v, k, last_in_parent)
    model.parent = parent
    return model


def build_model_raw(v, k: Optional[str], last_in_parent=True) -> JValueElement:
    if v is None:
        return JNull(None, k, last_in_parent)
    elif type(v) is str:
        return JString(v, k, last_in_parent)
    elif type(v) is int or type(v) is float:
        return JNumber(v, k, last_in_parent)
    elif type(v) is bool:
        return JBoolean(v, k, last_in_parent)
    elif type(v) is dict or type(v) is defaultdict:
        obj = JObject(v, k, last_in_parent)
        obj.set_elements(build_object_fields_models(v, obj))
        return obj
    elif type(v) is list:
        array = JArray(v, k, last_in_parent)
        array.set_elements(build_array_items_models(v, array))
        return array
    else:
        v.set_key(k)
        return v


def set_indent_recursive(model: JElement, indent: int):
    model.indent = indent
    if issubclass(type(model), JComplexElement):
        model.start.indent = indent
        model.end.indent = indent
        for e in model.elements:
            set_indent_recursive(e, indent + INDENT)


def build_object_fields_models(v, parent: JValueElement) -> List[JValueElement]:
    max_field_name_length = 0 if len(v) == 0 else max(len(k) for k in v)
    fields = []
    i = 0
    size = len(v)
    for k, v in v.items():
        model = build_model(v, k, i >= size - 1, parent)
        model.padding = max_field_name_length - len(k) + 1
        fields.append(model)
        i += 1
    return fields


def build_array_items_models(v, parent: JValueElement) -> List[JValueElement]:
    items = []
    size = len(v)
    for i, v in enumerate(v):
        items.append(build_model(v, i, i >= size - 1, parent))
        i += 1
    return items
