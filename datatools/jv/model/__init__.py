from datatools.jv.model.JBoolean import JBoolean
from datatools.jv.model.JElement import JElement
from datatools.jv.model.JFieldNull import JFieldNull
from datatools.jv.model.JNull import JNull
from datatools.jv.model.JNumber import JNumber
from datatools.jv.model.JObject import JObject
from datatools.jv.model.JObjectField import JObjectField
from datatools.jv.model.JObjectFields import JObjectFields
from datatools.jv.model.JString import JString

INDENT = 2


def set_attrs(model: JElement, indent: int, has_trailing_comma: bool):
    model.indent = indent
    model.has_trailing_comma = has_trailing_comma
    return model


def build_object_field_model(k: str, v, indent, has_trailing_comma) -> JObjectField:
    if v is None:
        return JFieldNull(k, indent, has_trailing_comma)


def build_object_fields_model(j, indent) -> JObjectFields:
    model = JObjectFields()

    model.fields = []
    i = 0
    size = len(j)
    for k, v in j.items():
        model.fields.append(build_object_field_model(k, v, indent, i < size - 1))
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
        model = JObject(indent, has_trailing_comma)
        model.fields = build_object_fields_model(j, indent + INDENT)

    model.indent = indent
    model.has_trailing_comma = has_trailing_comma
    return model
