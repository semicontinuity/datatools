from typing import List

from datatools.jv.model.JElement import JElement
from datatools.jv.model.JObjectField import JElement


class JObjectFields(JElement):
    fields: List[JElement]

    def __init__(self) -> None:
        self.fields = []

    def elements(self):
        for field in self.fields:
            yield from field.elements()
