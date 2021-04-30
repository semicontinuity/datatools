#!/usr/bin/env python3
from json import JSONDecodeError

from datatools.json.json_viz_helper import *
from datatools.json.structure_discovery import *
from datatools.util.html_util import *

tk = CustomHtmlToolkit()


def stderr_print(*args, **kwargs):
    import sys
    print(*args, file=sys.stderr, **kwargs)


def list_of_single_record(element, element_descriptor):
    return ListNode([node(element, element_descriptor)])


def list_of_multi_record(j, descriptor):
    return ListNode([node(j[index], descriptor.list[index]) for index in range(len(descriptor.list))])


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


class MatrixNode:
    def __init__(self, j, height, width):
        self.data = j
        self.height = height
        self.width = width

    def __str__(self):
        return div(
            span(f'Matrix {self.height} x {self.width}', clazz='header'),
            table(
                thead(
                    tr(
                        tk.custom_th('#'),
                        *[tk.custom_th(str(i)) for i in range(self.width)]
                    )
                ),
                tbody(
                    *[
                        tr(
                            tk.custom_th(str(y)),
                            *[
                                tk.td_value_with_color(cell, "a_v")  # all cells are primitives
                                for cell in sub_j
                            ]
                        )
                        for y, sub_j in enumerate(self.data)
                    ]
                ),
                clazz='m'
            ),
            clazz=('a', "collapsed2"), onclick='toggle2(this, "DIV")'
        ).__str__()


def node(j, descriptor):
    if descriptor.is_primitive():
        return str(j)
    elif descriptor.is_dict():
        return ObjectNode(j, descriptor, True)
    elif descriptor.is_list():
        return list_of_multi_record(j, descriptor)
    elif descriptor.is_array() and descriptor.length == 1 and descriptor.item.is_dict():
        return list_of_single_record(j[0], descriptor.item)
    elif descriptor.is_array():
        if descriptor.item.is_array() and descriptor.length is not None and descriptor.item.length is not None:
            return MatrixNode(j, descriptor.length, descriptor.item.length)
        # else:
        #     return ListNode(j, descriptor)
        pass


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
