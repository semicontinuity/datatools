from datatools.jv.model.JString import JString
from datatools.jv.model.JObjectFieldPrimitive import JObjectFieldPrimitive


class JFieldString(JObjectFieldPrimitive):
    value: str

    def __init__(self, value: str, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.value = value

    def __repr__(self):
        return JString.value_repr(self.value)

