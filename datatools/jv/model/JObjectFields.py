from typing import List

from datatools.jv.model.JObjectField import JElement


class JObjectFields(JElement):
    fields: List[JElement]

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.fields = []

    def elements(self):
        for field in self.fields:
            yield from field.elements()
