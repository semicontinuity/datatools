from datatools.jv.model.JElement import JElement


class JFieldArrayEnd(JElement):

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)

    def __repr__(self) -> str:
        return "]"
