from typing import Optional, Any

from datatools.json.util import is_primitive
from datatools.util.html.elements import *


class ListNode:
    def __init__(self, records, tk):
        self.records = records
        self.tk = tk

    def __str__(self):
        return self.html_numbered_table().__str__()

    def html_numbered_table(self):
        if all((is_primitive(record) for record in self.records)):
            return self.html_spans_table('regular' if len(self.records) < 150 else 'collapsed2')
        elif len(self.records) > 7 or len(str(self.records)) >= 250:
            return self.html_numbered_table_impl(collapsed=True)
        else:
            return self.html_numbered_table_impl(collapsed=False)

    def html_spans_table(self, clazz):
        return div(
            self.tk.possibly_overlayed_span(f'{len(self.records)} items', clazz="header", onclick='toggle2(this, "DIV")'),
            *[
                self.array_entry(pos, self.records[pos]) for pos in range(len(self.records))
            ],
            clazz=("a", clazz), onclick="toggle2(this, 'DIV')"
        )

    def array_entry(self, i: int, contents: Optional[Any]):
        return self.tk.possibly_overlayed_span(
            self.tk.possibly_overlayed_span(i, clazz='index'),
            self.tk.possibly_overlayed_span(contents, clazz='none' if contents is None else None),
            clazz='ae'
        )

    def html_numbered_table_impl(self, collapsed: bool):
        return table(
            thead(
                th(span('#'), clazz='a', onclick="toggle(this)"),
                th(span(f'{len(self.records)} items'), clazz='a')
            ) if collapsed else None,
            tbody(
                (
                    tr(th(span(pos), clazz='a'), self.tk.td_value_with_color(self.records[pos], "a_v"))
                    for pos in range(len(self.records))
                ),
                clazz="collapsed" if collapsed else None
            ),
            clazz="a"
        )
