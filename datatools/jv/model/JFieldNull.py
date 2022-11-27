from datatools.jv.model.JObjectFieldPrimitive import JObjectFieldPrimitive


class JFieldNull(JObjectFieldPrimitive):

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)

    def __repr__(self): return "null"
