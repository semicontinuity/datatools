from typing import List

from datatools.jv.model.JBoolean import JBoolean
from datatools.jv.model.JElement import JElement
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


def build_object_field_model(k: str, v, indent, has_trailing_comma) -> JObjectField:
    if v is None:
        return JFieldNull(k, indent, has_trailing_comma)
    elif type(v) is str:
        return JFieldString(v, k, indent, has_trailing_comma)
    elif type(v) is int or type(v) is float:
        return JFieldNumber(v, k, indent, has_trailing_comma)
    elif type(v) is bool:
        return JFieldBoolean(v, k, indent, has_trailing_comma)
    elif type(v) is dict:
        return JFieldObject(k, build_object_fields_model2(v, indent + INDENT), indent, has_trailing_comma)


def build_model(v, indent=0, has_trailing_comma=False) -> JElement:
    if v is None:
        return JNull(indent, has_trailing_comma)
    elif type(v) is str:
        return JString(v, indent, has_trailing_comma)
    elif type(v) is int or type(v) is float:
        return JNumber(v, indent, has_trailing_comma)
    elif type(v) is bool:
        return JBoolean(v, indent, has_trailing_comma)
    elif type(v) is dict:
        return JObject(build_object_fields_model2(v, indent + INDENT), indent, has_trailing_comma)


def build_object_fields_model2(j, indent) -> List[JObjectField]:
    fields = []
    i = 0
    size = len(j)
    for k, v in j.items():
        fields.append(build_object_field_model(k, v, indent, i < size - 1))
        i += 1
    return fields
