from datatools.jv.model.JPrimitiveElement import JPrimitiveElement


class JNull(JPrimitiveElement):

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)

    def __repr__(self):
        return "null"

