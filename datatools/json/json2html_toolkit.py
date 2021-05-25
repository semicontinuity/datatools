from datatools.json.json_viz_helper import *
from datatools.util.html_util import *


class HtmlToolkit:
    def page_node(self, j, descriptor):
        return PageNode(self.node(j, descriptor), "")

    def node(self, j, descriptor):
        if descriptor.is_primitive():
            return self.primitive(j)
        elif descriptor.is_dict():
            return self.object_node(j, descriptor)
        elif descriptor.is_list():
            return self.list_of_multi_record(j, descriptor)
        elif descriptor.is_array() and descriptor.length == 1 and descriptor.item.is_dict():
            return self.list_of_single_record(j[0], descriptor.item)
        elif descriptor.is_array():
            if descriptor.item.is_array() and descriptor.length is not None and descriptor.item.length is not None:
                return self.matrix_node(j, descriptor)
            # elif descriptor.item.is_dict() and descriptor.length is not None:
            #     return self.uniform_table_node(j, descriptor.item)

    def primitive(self, j):
        return str(j)

    def list_of_single_record(self, element, element_descriptor):
        return ListNode([self.node(element, element_descriptor)])

    def list_of_multi_record(self, j, descriptor):
        return ListNode([self.node(j[index], descriptor.list[index]) for index in range(len(descriptor.list))])

    def object_node(self, j, descriptor):
        return ObjectNode(j, descriptor, True, self)

    def matrix_node(self, j, descriptor):
        return MatrixNode(j, descriptor.length, descriptor.item.length)

    # def uniform_table_node(self, j, item_descriptor):
    #     return UniformTableNode(j, item_descriptor, self)


class ObjectNode:
    def __init__(self, j, descriptor, vertical, kit):
        self.fields = {key: kit.node(subj, descriptor.dict[key]) for key, subj in j.items()}
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
