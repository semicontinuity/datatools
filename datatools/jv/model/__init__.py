from typing import List, Optional

from datatools.jv.model.JArray import JArray
from datatools.jv.model.JBoolean import JBoolean
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JFieldArray import JFieldArray
from datatools.jv.model.JFieldBoolean import JFieldBoolean
from datatools.jv.model.JFieldNull import JFieldNull
from datatools.jv.model.JFieldNumber import JFieldNumber
from datatools.jv.model.JFieldObject import JFieldObject
from datatools.jv.model.JFieldString import JFieldString
from datatools.jv.model.JNull import JNull
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JObjectField import JObjectField
from datatools.jv.model.JString import JString

INDENT = 2


def build_object_field_model(parent: JElement, k: str, v, indent, has_trailing_comma) -> JObjectField:
    model = build_object_field_model_raw(k, v, indent, has_trailing_comma)
    model.parent = parent
    return model


def build_object_field_model_raw(k: str, v, indent, has_trailing_comma) -> JObjectField:
    if v is None:
        return JFieldNull(k, indent, has_trailing_comma)
    elif type(v) is str:
        return JFieldString(v, k, indent, has_trailing_comma)
    elif type(v) is int or type(v) is float:
        return JFieldNumber(v, k, indent, has_trailing_comma)
    elif type(v) is bool:
        return JFieldBoolean(v, k, indent, has_trailing_comma)
    elif type(v) is dict:
        obj = JFieldObject(k, indent, has_trailing_comma)
        obj.start.parent = obj
        obj.elements = build_object_fields_models(obj, v, indent + INDENT)
        obj.end.parent = obj
        return obj
    elif type(v) is list:
        array = JFieldArray(k, indent, has_trailing_comma)
        array.start.parent = array
        array.elements = build_array_items_models(array, v, indent + INDENT)
        array.end.parent = array
        return array


def build_model(parent: Optional[JElement], v, indent=0, has_trailing_comma=False) -> JElement:
    model = build_model_raw(v, indent, has_trailing_comma)
    model.parent = parent
    return model


def build_model_raw(v, indent=0, has_trailing_comma=False) -> JElement:
    if v is None:
        return JNull(indent, has_trailing_comma)
    elif type(v) is str:
        return JString(v, indent, has_trailing_comma)
    elif type(v) is int or type(v) is float:
        return JNumber(v, indent, has_trailing_comma)
    elif type(v) is bool:
        return JBoolean(v, indent, has_trailing_comma)
    elif type(v) is dict:
        obj = JObject(indent, has_trailing_comma)
        obj.start.parent = obj
        obj.elements = build_object_fields_models(obj, v, indent + INDENT)
        obj.end.parent = obj
        return obj
    elif type(v) is list:
        array = JArray(indent, has_trailing_comma)
        array.start.parent = array
        array.elements = build_array_items_models(array, v, indent + INDENT)
        array.end.parent = array
        return array


def build_object_fields_models(parent: JElement, j, indent: int) -> List[JObjectField]:
    fields = []
    i = 0
    size = len(j)
    for k, v in j.items():
        fields.append(build_object_field_model(parent, k, v, indent, i < size - 1))
        i += 1
    return fields


def build_array_items_models(parent: JElement, j, indent: int) -> List[JElement]:
    items = []
    i = 0
    size = len(j)
    for v in j:
        items.append(build_model(parent, v, indent, i < size - 1))
        i += 1
    return items
