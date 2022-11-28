from datatools.jv.model.JFieldObjectEnd import JFieldObjectEnd
from datatools.jv.model.JFieldObjectStart import JFieldObjectStart
from datatools.jv.model.JObjectField import JObjectField
from datatools.jv.model.JObjectFields import JObjectFields


class JFieldObject(JObjectField):
    start: JFieldObjectStart
    fields: JObjectFields
    end: JFieldObjectEnd

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.start = JFieldObjectStart(name, indent)
        self.end = JFieldObjectEnd(indent, has_trailing_comma)

    def elements(self):
        yield self.start
        yield from self.fields.elements()
        yield self.end
