from typing import Tuple, Any

from datatools.json.json2ansi_buffer import Buffer
from datatools.json.structure_discovery import Descriptor, DictDescriptor, compute_column_paths, ArrayDescriptor, \
    child_by_path, compute_row_paths
from datatools.util.logging import stderr_print
from datatools.util.table_util import *

MAX_PRIMITIVE_LENGTH = 80


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
        elif descriptor.is_array() and descriptor.length == 1 and descriptor.item.is_dict():
            return self.list_of_single_record(j[0], descriptor.item)    # TODO: add [0] to show that it's a list
        elif descriptor.is_array():
            # if descriptor.item.is_array() and descriptor.length is not None and descriptor.item.length is not None:
            #     return self.matrix_node(j, descriptor)

            if descriptor.item.is_array():
                return self.uniform_table_node2(j, descriptor)
            if descriptor.item.is_dict() and descriptor.length is not None:
                return self.uniform_table_node(j, descriptor)
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

    def uniform_table_node(self, j, descriptor):
        item_descriptor = descriptor.item
        # column_headers = HBox([HeaderNode(column_name, False) for column_name in item_descriptor.dict])
        # body = RegularTable([
        #     HBox([self.node(entry[col_name], col_desc) for col_name, col_desc in item_descriptor.dict.items()])
        #     for i, entry in enumerate(j)
        # ])

        row_headers = VBox([HeaderNode(i, True) for i in range(len(j))])
        column_headers = column_headers_node_for_descriptor(item_descriptor, False)
        # column_headers.set_level_heights(column_headers.max_level_heights())
        paths = compute_column_paths(item_descriptor)
        body = RegularTable([
            HBox([
                self.node(child_by_path(row, path)[1], descriptor_by_path(item_descriptor, path)) for path in paths
            ])
            for index, row in enumerate(j)
        ])

        return ComplexTableNode(body, column_headers, row_headers)

    def uniform_table_node2(self, j, descriptor: ArrayDescriptor):
        row_paths = compute_row_paths(j ,descriptor)
        item_descriptor = descriptor.inner_item()
        column_paths = compute_column_paths(item_descriptor)

        row_headers = row_headers_node_for_descriptor(j, descriptor, True)
        row_headers.set_level_widths(row_headers.max_level_widths())

        body = RegularTable([
            self.uniform_table_node2_tr(child_by_path(j, row_path)[1], item_descriptor, column_paths)
            for row_path in row_paths
        ])

        column_headers = column_headers_node_for_descriptor(item_descriptor, False)
        # column_headers.set_level_heights(column_headers.max_level_heights())

        return ComplexTableNode(body, column_headers, row_headers)

    def uniform_table_node2_tr(self, row, row_descriptor, column_paths):
        return HBox([
            self.node(child_by_path(row, path)[1], descriptor_by_path(row_descriptor, path))
            for path in column_paths
        ])


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
            return j if len(j) <= MAX_PRIMITIVE_LENGTH else '...', Buffer.MASK_NONE
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
    def __init__(self, body: RegularTable, column_headers, row_headers):
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


def descriptor_by_path(d: Descriptor, path: Tuple[str]) -> Any:
    for name in path:
        d = d.dict[name]
    return d


def column_headers_node_for_descriptor(descriptor: DictDescriptor, vertical: bool, leaf_sink: List = None, name=None):
    leaf_sink = leaf_sink if leaf_sink is not None else []
    if descriptor.is_dict():
        nodes = [column_headers_node_for_descriptor(d, vertical, leaf_sink, name) for name, d in descriptor.dict.items()]
        if name is None:
            return (NestedRowHeaders if vertical else NestedColumnHeaders)(nodes, leaf_sink)
        else:
            return (HBox if vertical else VBox)([
                HeaderNode(name, False), (VBox if vertical else HBox)(nodes)
            ])
    else:
        leaf = HeaderNode(name, False)
        leaf_sink.append(leaf)
        return leaf


def row_headers_node_for_descriptor(j, descriptor: ArrayDescriptor, vertical: bool, leaf_sink: List = None, name=None):
    leaf_sink = leaf_sink if leaf_sink is not None else []
    if descriptor.is_array():
        nodes = [row_headers_node_for_descriptor(jj, descriptor.item, vertical, leaf_sink, name) for name, jj in descriptor.items(j)]
        if name is None:
            return (NestedRowHeaders if vertical else NestedColumnHeaders)(nodes, leaf_sink)
        else:
            return (HBox if vertical else VBox)([
                HeaderNode(name, type(name) is int), (VBox if vertical else HBox)(nodes)
            ])
    else:
        leaf = HeaderNode(name, type(name) is int)
        leaf_sink.append(leaf)
        return leaf


class NestedColumnHeaders(HBox):
    leaves: List[Block]

    def __init__(self, contents, leaves: List[Block]):
        super().__init__(contents)
        self.leaves = leaves

    def compute_widths(self) -> List[int]:
        super(NestedColumnHeaders, self).compute_widths()
        return [leaf.width for leaf in self.leaves]

    def set_min_widths(self, sizes: List[int]):
        for i in range(len(sizes)):
            self.leaves[i].set_min_width(sizes[i])

    def max_level_heights(self) -> List[int]:
        result = []
        self.max_level_heights0(result, 0, self.contents)
        return result

    def max_level_heights0(self, sizes: List[int], index: int, contents: List[HBox]):
        if index >= len(sizes):
            sizes.append(0)
        for block in contents:
            if type(block) is HeaderNode:
                sizes[index] = max(sizes[index], block.height)
            else:
                sizes[index] = max(sizes[index], block.contents[0].height)
                self.max_level_heights0(sizes, index + 1, block.contents[1].contents)

    def set_level_heights(self, sizes: List[int]):
        self.set_level_heights0(sizes, 0, self.contents)

    def set_level_heights0(self, sizes: List[int], index: int, contents: List[HBox]):
        for block in contents:
            if type(block) is HeaderNode:
                block.set_min_height(sizes[index])
            else:
                block.contents[0].set_min_height(sizes[index])
                self.set_level_heights0(sizes, index + 1, block.contents[1].contents)

class NestedRowHeaders(VBox):
    leaves: List[Block]

    def __init__(self, contents, leaves: List[Block]):
        super().__init__(contents)
        self.leaves = leaves

    def compute_widths(self) -> List[int]:
        super(NestedRowHeaders, self).compute_widths()
        return [leaf.width for leaf in self.leaves]

    def set_min_heights(self, sizes: List[int]):
        for i in range(len(sizes)):
            self.leaves[i].set_min_height(sizes[i])

    def max_level_widths(self) -> List[int]:
        result = []
        self.max_level_widths0(result, 0, self.contents)
        return result

    def max_level_widths0(self, widths: List[int], index: int, contents: List[HBox]):
        if index >= len(widths):
            widths.append(0)
        for block in contents:
            if type(block) is HeaderNode:
                widths[index] = max(widths[index], block.width)
            else:
                widths[index] = max(widths[index], block.contents[0].width)
                self.max_level_widths0(widths, index + 1, block.contents[1].contents)

    def set_level_widths(self, sizes: List[int]):
        self.set_level_widths0(sizes, 0, self.contents)

    def set_level_widths0(self, sizes: List[int], index: int, contents: List[HBox]):
        for block in contents:
            if type(block) is HeaderNode:
                block.set_min_width(sizes[index])
            else:
                block.contents[0].set_min_width(sizes[index])
                self.set_level_widths0(sizes, index + 1, block.contents[1].contents)