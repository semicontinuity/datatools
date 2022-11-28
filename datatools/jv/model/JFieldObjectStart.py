from datatools.jv.model.JElement import JElement


class JFieldObjectStart(JElement):
    name: str

    def __init__(self, name: str, indent=0) -> None:
        super().__init__(indent)
        self.name = name

    def __str__(self):
        return ' ' * self.indent + f'"{self.name}": {{'
