from datatools.jv.model.JObjectField import JObjectField
from datatools.jv.model.JElement import JElement


class JFieldArrayStart(JElement):
    name: str

    def __init__(self, name: str, indent=0) -> None:
        super().__init__(indent)
        self.name = name

    def __str__(self):
        return ' ' * self.indent + JObjectField.field_name_repr(self.name) + '['
