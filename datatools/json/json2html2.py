#!/usr/bin/env python3

from json import JSONDecodeError

from datatools.json.json_viz_helper import *
from datatools.json.structure_discovery import *
from datatools.json.util import is_primitive
from datatools.util.html_util import *

tk = CustomHtmlToolkit()


def stderr_print(*args, **kwargs):
    import sys
    print(*args, file=sys.stderr, **kwargs)


class ListNode:
    def __init__(self, j, descriptor):
        self.records = [node(j[index], descriptor.list[index]) for index in range(len(descriptor.list))]

    def __str__(self):
        return self.html_numbered_table().__str__()

    def html_numbered_table(self):
        if all((is_primitive(record) for record in self.records)):
            return self.html_spans_table('regular' if len(self.records) < 150 else 'collapsed2')
        elif len(self.records) > 7 or len(str(self.records)) >= 250:
            return self.html_numbered_table_collapsed()
        else:
            return self.html_numbered_table_plain()

    def html_spans_table(self, clazz):
        return div(
            tk.custom_span(f'{len(self.records)} items', clazz="header", onclick='toggle2(this, "DIV")'),
            *[
                self.array_entry(pos + 1, self.records[pos]) for pos in range(len(self.records))
            ],
            clazz=("a", clazz), onclick="toggle2(this, 'DIV')"
        )

    @staticmethod
    def array_entry(i: int, contents: Optional[Any]):
        return tk.custom_span(
            tk.custom_span(i, clazz='index'),
            tk.custom_span(contents, clazz='none' if contents is None else None),
            clazz='ae'
        )

    def html_numbered_table_plain(self):
        return table(
            *[
                tr(Element('th', pos + 1, clazz='a'), tk.td_value_with_color(self.records[pos], "a_v"))
                for pos in range(len(self.records))
            ],
            clazz="a"
        )

    def html_numbered_table_collapsed(self):
        return table(
            thead(
                tk.custom_th('#', onclick="toggle(this)"),
                tk.custom_th(f'{len(self.records)} items')
            ),
            tbody(
                *[
                    tr(tk.custom_th(str(pos + 1)), tk.td_value_with_color(self.records[pos], "a_v"))
                    for pos in range(len(self.records))
                ],
                clazz="collapsed"
            ),
            clazz="a"
        )


class ObjectNode:
    def __init__(self, j, descriptor, vertical):
        self.fields = {key: node(subj, descriptor.dict[key]) for key, subj in j.items()}
        self.vertical = vertical

    def __str__(self):
        return self.vertical_html().__str__() if self.vertical else self.horizontal_html().__str__()

    def horizontal_html(self):
        return table(
            *[
                thead(
                    *[tk.custom_th(key) for key in self.fields]
                ),
                tr(
                    *[td(value) for value in self.fields.values()]
                )
            ],
            clazz="oh"
        )

    def vertical_html(self):
        return table(*[self.vertical_html_tr(key, value) for key, value in self.fields.items()], clazz="ov")

    @staticmethod
    def vertical_html_tr(key, value):
        return tr(tk.custom_th(key, clazz='ov_th'), tk.td_value_with_color(value, "ov_v"))


def node(j, descriptor):
    if descriptor.is_primitive():
        return str(j)
    elif descriptor.is_dict():
        return ObjectNode(j, descriptor, True)
    elif descriptor.is_list():
        return ListNode(j, descriptor)


def main():
    import json, sys

    # j = json.load(sys.stdin)
    lines = [line for line in sys.stdin]
    s = ''.join(lines)
    j = json.loads(s)

    d = Discovery().object_descriptor(j)
    print(PageNode(node(j, d), ""))


if __name__ == "__main__":
    try:
        main()
    except JSONDecodeError as ex:
        stderr_print("Reads json. Outputs html.")
