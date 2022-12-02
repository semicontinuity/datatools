from datatools.jv.model.JElement import JElement


class JObjectField(JElement):
    """ Object's field (complete) """

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.name = name
