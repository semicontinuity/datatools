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


def build_model(v, k: Optional[str] = None, indent: int = 0, last_in_parent=True,
                parent: Optional[JElement] = None) -> JValueElement:
    model = build_model_raw(v, k, indent, last_in_parent)
    model.parent = parent
    return model


def build_model_raw(v, k: Optional[str], indent: int, last_in_parent=True) -> JValueElement:
    if v is None:
        return JNull(None, k, indent, last_in_parent)
    elif type(v) is str:
        return JString(v, k, indent, last_in_parent)
    elif type(v) is int or type(v) is float:
        return JNumber(v, k, indent, last_in_parent)
    elif type(v) is bool:
        return JBoolean(v, k, indent, last_in_parent)
    elif type(v) is dict:
        obj = JObject(k, indent, last_in_parent)
        obj.set_elements(build_object_fields_models(v, indent + INDENT, obj))
        return obj
    elif type(v) is list:
        array = JArray(k, indent, last_in_parent)
        array.set_elements(build_array_items_models(v, indent + INDENT, array))
        return array


def build_object_fields_models(v, indent: int, parent: JValueElement) -> List[JValueElement]:
    max_field_name_length = 0 if len(v) is 0 else max(len(k) for k in v)
    fields = []
    i = 0
    size = len(v)
    for k, v in v.items():
        model = build_model(v, k, indent, i >= size - 1, parent)
        model.padding = max_field_name_length - len(k) + 1
        fields.append(model)
        i += 1
    return fields


def build_array_items_models(v, indent: int, parent: JValueElement) -> List[JValueElement]:
    items = []
    i = 0
    size = len(v)
    for v in v:
        items.append(build_model(v, None, indent, i >= size - 1, parent))
        i += 1
    return items
