from datatools.jv.model.JObjectField import JObjectField


class JObjectFieldPrimitive(JObjectField):
    """ Object's field (complete) """
    name: str

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.name = name

    def elements(self):
        yield self

    def __str__(self):
        return ' ' * self.indent + f'"{self.name}": ' + repr(self) + (',' if self.has_trailing_comma else '')
