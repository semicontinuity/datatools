from typing import List, Optional

from datatools.jv.model.JArray import JArray
from datatools.jv.model.JBoolean import JBoolean
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JNull import JNull
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JString import JString
from datatools.jv.model.JValueElement import JValueElement

INDENT = 2


def build_model(parent: Optional[JElement], k: Optional[str], v, indent=0, has_trailing_comma=False) -> JValueElement:
    model = build_model_raw(k, v, indent, has_trailing_comma)
    model.parent = parent
    model.collapsed = True
    return model


def build_model_raw(k: Optional[str], v, indent, has_trailing_comma) -> JValueElement:
    if v is None:
        return JNull(k, None, indent, has_trailing_comma)
    elif type(v) is str:
        return JString(k, v, indent, has_trailing_comma)
    elif type(v) is int or type(v) is float:
        return JNumber(k, v, indent, has_trailing_comma)
    elif type(v) is bool:
        return JBoolean(k, v, indent, has_trailing_comma)
    elif type(v) is dict:
        obj = JObject(k, indent, has_trailing_comma)
        obj.set_elements(build_object_fields_models(obj, v, indent + INDENT))
        return obj
    elif type(v) is list:
        array = JArray(k, indent, has_trailing_comma)
        array.set_elements(build_array_items_models(array, v, indent + INDENT))
        return array


def build_object_fields_models(parent: JValueElement, j, indent: int) -> List[JValueElement]:
    max_field_name_length = 0 if len(j) is 0 else max(len(k) for k in j)
    fields = []
    i = 0
    size = len(j)
    for k, v in j.items():
        model = build_model(parent, k, v, indent, i < size - 1)
        model.padding = max_field_name_length - len(k) + 1
        fields.append(model)
        i += 1
    return fields


def build_array_items_models(parent: JValueElement, j, indent: int) -> List[JValueElement]:
    items = []
    i = 0
    size = len(j)
    for v in j:
        items.append(build_model(parent, None, v, indent, i < size - 1))
        i += 1
    return items
