from typing import List, Tuple, AnyStr

from datatools.jv.highlighting.highlighting import Highlighting
from datatools.jv.highlighting.rich_text import Style
from datatools.jv.model.JFieldObjectEnd import JFieldObjectEnd
from datatools.jv.model.JFieldObjectStart import JFieldObjectStart
from datatools.jv.model.JObjectField import JObjectField


class JFieldObject(JObjectField):
    start: JFieldObjectStart
    fields: List[JObjectField]
    end: JFieldObjectEnd
    collapsed: bool

    def __init__(self, name: str, indent=0, has_trailing_comma=False) -> None:
        super().__init__(name, indent, has_trailing_comma)
        self.start = JFieldObjectStart(name, indent)
        self.end = JFieldObjectEnd(indent, has_trailing_comma)
        self.collapsed = False

    def __iter__(self):
        if self.collapsed:
            yield self
        else:
            yield self.start
            for field in self.fields:
                yield from field
            yield self.end

    def spans(self) -> List[Tuple[AnyStr, Style]]:
        """ (Used only if in collapsed state) """
        return JObjectField.spans_for_field_name(self.indent, self.name) + [('{…}', Highlighting.CURRENT.for_curly_braces())]

    def layout(self, line: int) -> int:
        if self.collapsed:
            return super().layout(line)
        else:
            self.line = line
            line = self.start.layout(line)
            for item in self.fields:
                line = item.layout(line)
            return self.end.layout(line)
