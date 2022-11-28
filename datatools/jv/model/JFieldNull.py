from datatools.jv.highlighting.ansi_colors import Highlighting
from datatools.jv.model.JObjectFieldPrimitive import JObjectFieldPrimitive


class JFieldNull(JObjectFieldPrimitive):

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)

    def __repr__(self): return Highlighting.CURRENT.ansi_set_attrs_null() + "null"
