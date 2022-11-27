from typing import Dict

from datatools.jv.model.JBoolean import JBoolean
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JNull import JNull
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JString import JString


def set_attrs(model: JElement, indent: int, has_trailing_comma: bool):
    model.indent = indent
    model.has_trailing_comma = has_trailing_comma
    return model


def build_object_model(j, indent, has_trailing_comma) -> JObject:
    model = JObject()
    set_attrs(model, indent, has_trailing_comma)
    return model


def build_model(j, indent=0, has_trailing_comma=False) -> JElement:
    model = None

    if j is None:
        model = JNull()
    elif type(j) is str:
        model = JString(j)
    elif type(j) is int:
        model = JNumber(j)
    elif type(j) is float:
        model = JNumber(j)
    elif type(j) is bool:
        model = JBoolean(j)
    elif type(j) is dict:
        model = JObject()

    model.indent = indent
    model.has_trailing_comma = has_trailing_comma
    return model
