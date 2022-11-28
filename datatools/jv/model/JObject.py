from datatools.jv.model import JElement
from datatools.jv.model.JObjectEnd import JObjectEnd
from datatools.jv.model.JObjectFields import JObjectFields
from datatools.jv.model.JObjectStart import JObjectStart


class JObject(JElement):
    """ Top-level object """
    start: JObjectStart
    fields: JObjectFields
    end: JObjectEnd

    def __init__(self, indent=0, has_trailing_comma=False) -> None:
        super().__init__(indent, has_trailing_comma)
        self.start = JObjectStart(indent)
        self.end = JObjectEnd(indent, has_trailing_comma)

    def elements(self):
        yield self.start
        yield from self.fields.elements()
        yield self.end

