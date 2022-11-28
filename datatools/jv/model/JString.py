from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JString(JPrimitiveElement):
    value: str

    def __init__(self, value, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.value = value

    def __repr__(self):
        return JString.value_repr(self.value)

    @staticmethod
    def value_repr(value):
        return Highlighting.CURRENT.ansi_set_attrs_string() + '"' + ''.join([JString.escape(c) for c in value]) + '"'

    @staticmethod
    def escape(c: str):
        if c == '\b': return "\\b"
        if c == '\t': return "\\t"
        if c == '\n': return "\\n"
        if c == '\r': return "\\r"
        if c == '\\': return "\\\\"
        if c == '"': return "\\\""
        # Add unicode stuff?
        return c
