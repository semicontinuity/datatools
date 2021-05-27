from typing import Tuple, Any

from datatools.json.json2ansi_buffer import Buffer
from datatools.json.structure_discovery import Descriptor, DictDescriptor, compute_paths_of_leaves
from datatools.util.logging import stderr_print
from datatools.util.table_util import *


class AnsiToolkit:
    def page_node(self, j, descriptor):
        return PageNode(self.node(j, descriptor), "")

    def node(self, j, descriptor):
        if descriptor.is_primitive():
            return self.primitive(j)
        elif descriptor.is_dict():
            return self.object_node(j.items(), lambda key: descriptor.dict[key])
        elif descriptor.is_list():
            return self.list_of_multi_record(j, descriptor)
        # elif descriptor.is_array() and descriptor.length == 1 and descriptor.item.is_dict():
        #     return self.list_of_single_record(j[0], descriptor.item)
        elif descriptor.is_array():
            # if descriptor.item.is_array() and descriptor.length is not None and descriptor.item.length is not None:
            #     return self.matrix_node(j, descriptor)
            if descriptor.item.is_dict() and descriptor.length is not None:
                return self.uniform_table_node(j, descriptor.item)
            else:
                if type(j) is dict:
                    return self.object_node(j.items(), lambda key: descriptor.item)
                else:
                    return self.array(j, descriptor)
        else:
            stderr_print(type(descriptor))

    def primitive(self, j):
        return PrimitiveNode(j)

    def list_of_single_record(self, element, element_descriptor):
        return self.object_node(element.items(), lambda key: element_descriptor.dict[key])

    def list_of_multi_record(self, j, descriptor):
        return EntriesNode(enumerate(j), lambda key: descriptor.list[key], self, True)

    def array(self, j, descriptor):
        return EntriesNode(enumerate(j), lambda key: descriptor.item, self, True)

    def object_node(self, items, descriptor_f):
        return EntriesNode(items, descriptor_f, self, False)

    def matrix_node(self, j, descriptor):
        return self.array(j, descriptor)

    def uniform_table_node(self, j, item_descriptor):
        column_headers = HBox([HeaderNode(column_name, False) for column_name in item_descriptor.dict])
        row_headers = VBox([HeaderNode(i, True) for i in range(len(j))])
        body = RegularTable([
            HBox([self.node(entry[col_name], col_desc) for col_name, col_desc in item_descriptor.dict.items()])
            for i, entry in enumerate(j)
        ])
        # return header_node_for_descriptor(item_descriptor, True)
        return ComplexTableNode(column_headers, row_headers, body)
        # return ComplexTableNode(j, item_descriptor, self)


class PageNode:
    def __init__(self, root, title):
        self.root = root
        self.title = title

    def layout(self):
        self.root.compute_width()
        self.root.compute_height()
        self.root.compute_position(0, 0)

    def paint(self):
        self.layout()
        buffer = Buffer(self.root.width, self.root.height)
        self.root.paint(buffer)
        return buffer


class TextCell(Block):
    def __init__(self, text, mask = 0):
        self.text = text
        self.mask = mask
        self.width = len(text) + 2
        self.height = 1

    def paint(self, buffer):
        # background
        if self.mask != 0:
            buffer.draw_attrs_box(self.x, self.y, self.width, self.height, self.mask)

        # top border
        buffer.draw_attrs_box(self.x, self.y, self.width, 1, Buffer.MASK_OVERLINE)

        # left border
        for j in range(self.height):
            buffer.draw_text(self.x, self.y + j, '▏')

        buffer.draw_text(self.x + 1, self.y, self.text)


class HeaderNode(TextCell):
    def __init__(self, key, is_array):
        super().__init__(str(key), self.attr_for(is_array))

    @staticmethod
    def attr_for(is_array):
        if is_array:
            return Buffer.MASK_FG_EMPHASIZED | Buffer.MASK_BG_EMPHASIZED | Buffer.MASK_BOLD
        else:
            return Buffer.MASK_FG_EMPHASIZED | Buffer.MASK_BG_EMPHASIZED


class PrimitiveNode(TextCell):
    def __init__(self, j):
        super().__init__(*self.text_and_mask_for(j))

    @staticmethod
    def text_and_mask_for(j):
        primitive_type = type(j)
        if primitive_type is type(None):
            return 'null', Buffer.MASK_ITALIC
        elif primitive_type is bool:
            return str(j).lower(), Buffer.MASK_ITALIC | Buffer.MASK_BOLD
        elif primitive_type is str:
            return j if len(j) <= 80 else '...', Buffer.MASK_NONE
        else:
            return str(j), Buffer.MASK_BOLD


class CompositeTableNode(RegularTable):
    def __init__(self, contents: List):
        super().__init__(contents)

    @staticmethod
    def consolidate_width(corner, row_headers):
        corner.set_min_width(row_headers.width)
        row_headers.set_min_width(corner.width)

    @staticmethod
    def consolidate_height(column_headers, corner):
        column_headers.set_min_height(corner.height)
        corner.set_min_height(column_headers.height)

    @staticmethod
    def consolidate_min_widths(container1, container2):
        widths1 = container1.compute_widths()
        widths2 = container2.compute_widths()
        container2.set_min_widths(widths1)
        container1.set_min_widths(widths2)

    @staticmethod
    def consolidate_min_heights(container1, container2):
        heights1 = container1.compute_heights()
        heights2 = container2.compute_heights()
        container2.set_min_heights(heights1)
        container1.set_min_heights(heights2)

    def paint(self, buffer):
        self.paint_border(buffer)
        super().paint(buffer)   # contents

    def paint_border(self, buffer):
        # top border (in case there is no contents that normally paints the border)
        buffer.draw_attrs_box(self.x, self.y, self.width, 1, Buffer.MASK_OVERLINE)

        # left border (in case there is no contents that normally paints the border)
        for j in range(self.height):
            buffer.draw_text(self.x, self.y + j, '▏')


class EntriesNode(CompositeTableNode):
    def __init__(self, entries, descriptor_f, kit, is_array):
        super().__init__(
            [
                HBox([
                    HeaderNode(key, is_array), kit.node(subj, descriptor_f(key))
                ])
                for key, subj in entries
            ]
        )


class ComplexTableNode(CompositeTableNode):
    def __init__(self, column_headers, row_headers, body: RegularTable):
        corner = HeaderNode('#', False)

        self.consolidate_min_widths(body, column_headers)
        self.consolidate_min_heights(body, row_headers)

        row_headers.compute_width()
        self.consolidate_width(corner, row_headers)

        column_headers.compute_height()
        self.consolidate_height(column_headers, corner)

        super().__init__(
            [
                HBox([corner, column_headers]),
                HBox([row_headers, body])
            ]
        )


class ComplexTableNode2(CompositeTableNode):
    def __init__(self, j, entry_descriptor: DictDescriptor, kit):
        paths = compute_paths_of_leaves(entry_descriptor)
        super().__init__(
            [
                HBox([HeaderNode('#', False), header_node_for_descriptor(entry_descriptor)])
            ]
            +
            [
                HBox(
                    [HeaderNode(str(index), True)]
                    +
                    [kit.node(self.child_by_path(row, path), self.descriptor_by_path(entry_descriptor, path)) for path in paths]
                ) for index, row in enumerate(j)
            ]
        )

    def child_by_path(self, value: Any, path: Tuple[str]) -> Any:
        for name in path:
            if value is None:
                return None
            if isinstance(value, dict):
                value = value.get(name)
        return value

    def descriptor_by_path(self, d: Descriptor, path: Tuple[str]) -> Any:
        for name in path:
            d = d.dict[name]
        return d


def header_node_for_descriptor(descriptor: DictDescriptor, vertical: bool, name=None):
    if descriptor.is_dict():
        if name is None:
            return (NestedRowHeaders if vertical else NestedColumnHeaders)(
                [header_node_for_descriptor(d, vertical, name) for name, d in descriptor.dict.items()]
            )
        else:
            return (HBox if vertical else VBox)([
                HeaderNode(name, False),
                (VBox if vertical else HBox)([header_node_for_descriptor(d, vertical, name) for name, d in descriptor.dict.items()])
            ])
    else:
        return HeaderNode(name, False)


class NestedColumnHeaders(HBox):
    def __init__(self, contents):
        super().__init__(contents)


class NestedRowHeaders(VBox):
    def __init__(self, contents):
        super().__init__(contents)
