from typing import AnyStr

from datatools.json.coloring import ColumnAttrs, compute_column_attrs, compute_cross_column_attrs, hash_to_rgb_dark, \
    hash_code
from datatools.json.structure_discovery import *
from datatools.tui.box_drawing_chars import LEFT_BORDER
from datatools.tui.buffer.json2ansi_buffer import Buffer
from datatools.util.logging import stderr_print, debug
from datatools.util.table_util import *
from datatools.util.text_util import geometry


@dataclass
class BorderStyle:
    top: bool = False


@dataclass
class Style:
    table: BorderStyle
    header: BorderStyle
    cell: BorderStyle
    background_color: Optional[List[int]]


class AnsiToolkit:
    discovery: Discovery
    style: Style

    def __init__(self, discovery, style: Style, primitive_max_width=64):
        self.discovery = discovery
        self.style = style
        self.primitive_max_width = primitive_max_width
        AnsiToolkit.instance = self

    def page_node(self, j):
        return PageNode(self.block(j), "", self.style.background_color)

    def block(self, j):
        return self.node(j, self.discovery.object_descriptor(j))

    def node(self, j, descriptor: Descriptor) -> Block:
        debug("node", j=j)
        if descriptor.is_any():
            debug("node", descriptor={"is_any": True})
            descriptor = self.discovery.object_descriptor(j)

        if descriptor.is_primitive():
            debug("node", descriptor={"is_primitive": True})
            return self.primitive(j)

        if not descriptor.is_not_empty():
            debug("node", descriptor={"is_empty": True})
            return self.empty()

        elif descriptor.is_uniform():
            debug("node", descriptor={"is_uniform": True})
            # if descriptor.item.is_uniform() and descriptor.length is not None and descriptor.item.length is not None:
            #     return self.matrix_node(j, descriptor)

            if descriptor.is_not_empty() \
                    and descriptor.item_is_uniform() \
                    and not descriptor.item_is_dict() \
                    and descriptor.length is not None \
                    and descriptor.length > 1 \
                    and type(descriptor.inner_item()) is not AnyDescriptor:
                return self.uniform_table_node2(j, descriptor)
            if descriptor.is_not_empty() \
                    and descriptor.item_is_dict() \
                    and descriptor.length is not None \
                    and descriptor.length > 1:
                return self.uniform_table_node(j, descriptor)
            else:
                if type(j) is dict:
                    return self.object_node(j.items(), descriptor.entry)
                elif len(j) > 1:
                    return self.array(j, descriptor)
        if descriptor.is_dict():
            debug("node", descriptor={"is_dict": True})
            return self.object_node(j.items(), lambda key: descriptor.items()[key]) if j else self.empty()
        elif descriptor.is_list() and len(j) == 1 and descriptor.item.is_dict():
            debug("node", descriptor={"is_list": True, "length": 1})
            return self.list_of_single_record(j[0], descriptor.item)    # TODO: add [0] to show that it's a list
        elif descriptor.is_list():
            debug("node", descriptor={"is_list": True})
            return self.list_of_multi_record(j, descriptor)
        elif descriptor.is_uniform() and descriptor.length == 1 and descriptor.item.is_dict():
            debug("node", descriptor={"is_uniform":True, "is_list": True, "length": 1})
            return self.list_of_single_record(j[0], descriptor.item)    # TODO: add [0] to show that it's a list
        else:
            stderr_print(type(descriptor))

    def empty(self):
        return PrimitiveNode('')

    def primitive(self, j, attrs: ColumnAttrs = None):
        return PrimitiveNode(j, attrs)

    def list_of_single_record(self, element, element_descriptor):
        return HBox([
            HeaderNode('0', True),
            self.object_node(element.items(), element_descriptor.entry)
        ])

    def list_of_multi_record(self, j, descriptor):
        return EntriesNode(enumerate(j), descriptor.entry, self, True)

    def array(self, j, descriptor):
        return EntriesNode(enumerate(j), lambda key: descriptor.item, self, len(j) > 1) # hack

    def object_node(self, items, descriptor_f):
        return EntriesNode(items, descriptor_f, self, False)

    def matrix_node(self, j, descriptor):
        return self.array(j, descriptor)

    def uniform_table_node(self, j, descriptor):
        debug("uniform_table_node")
        item_descriptor = descriptor.item
        # column_headers = HBox([HeaderNode(column_name, False) for column_name in item_descriptor.dict])
        # body = RegularTable([
        #     HBox([self.node(entry[col_name], col_desc) for col_name, col_desc in item_descriptor.dict.items()])
        #     for i, entry in enumerate(j)
        # ])

        row_headers = VBox([HeaderNode(k, True) for k, v in descriptor.enumerate_entries(j)])
        column_headers = column_headers_node_for_descriptor(item_descriptor, False)
        # column_headers.set_level_heights(column_headers.max_level_heights())
        column_paths = compute_column_paths(item_descriptor)

        rows = [row for index, row in descriptor.enumerate_entries(j)]
        column_id_to_attrs: Dict[Hashable, ColumnAttrs] = {}
        for column_path in column_paths:
            if descriptor_by_path(item_descriptor, column_path).is_primitive():
                column_id_to_attrs[column_path] = compute_column_attrs(rows, column_path, child_by_path)
        compute_cross_column_attrs(rows, column_id_to_attrs, child_by_path)

        body = RegularTable([
            HBox([
                self.uniform_table_cell_node(row, item_descriptor, path, column_id_to_attrs.get(path)) for path in column_paths
            ])
            for index, row in descriptor.enumerate_entries(j)
        ])

        return ComplexTableNode(body, column_headers, row_headers)

    def uniform_table_node2(self, j, descriptor: Descriptor):
        debug("uniform_table_node2", descriptor=type(descriptor))
        row_paths = compute_row_paths(j, descriptor)
        # item_descriptor = descriptor.inner_item()
        item_descriptor = descriptor.item
        debug("uniform_table_node2", item_descriptor=item_descriptor)
        column_paths = compute_column_paths(item_descriptor)

        row_headers = row_headers_node_for_paths(j, descriptor)
        # row_headers = row_headers_node_for_descriptor(j, descriptor)
        row_headers.set_level_widths(row_headers.max_level_widths())

        rows = [child_by_path(j, row_path) for row_path in row_paths]

        column_id_to_attrs: Dict[Hashable, ColumnAttrs] = {}
        for column_path in column_paths:
            if descriptor_by_path(item_descriptor, column_path).is_primitive():
                column_id_to_attrs[column_path] = compute_column_attrs(rows, column_path, child_by_path)
        compute_cross_column_attrs(rows, column_id_to_attrs, child_by_path)

        body = RegularTable([
            self.uniform_table_node2_tr(row, item_descriptor, column_paths, column_id_to_attrs)
            for row in rows
        ])

        column_headers = column_headers_node_for_descriptor(item_descriptor, False)
        # column_headers.set_level_heights(column_headers.max_level_heights())

        return ComplexTableNode(body, column_headers, row_headers)

    def uniform_table_node2_tr(self, row, row_descriptor, column_paths, column_id_to_attrs):
        return HBox([
            self.uniform_table_cell_node(row, row_descriptor, path, column_id_to_attrs.get(path))
            for path in column_paths
        ])

    def uniform_table_cell_node(self, row, item_descriptor, path, attrs: ColumnAttrs = None):
        child = child_by_path(row, path)
        if child is ...:
            return self.empty()
        else:
            d = descriptor_by_path(item_descriptor, path)
            if d.is_primitive():
                return self.primitive(child, attrs)
            else:
                return self.node(child, d)


class PageNode:
    def __init__(self, root: Block, title, background_color: Optional[List[int]] = None):
        self.root = root
        self.title = title
        self.background_color = background_color

    def layout(self):
        self.root.compute_width()
        self.root.compute_height()
        self.root.compute_position(0, 0)

    def paint(self) -> Buffer:
        self.layout()
        buffer = Buffer(self.root.width, self.root.height, self.background_color)
        self.root.paint(buffer)
        return buffer


class TextCell(Block):
    def __init__(self, text: AnyStr, mask: int, border_style: BorderStyle, bg: Tuple[int, int, int] = None):
        width, height = geometry(text)
        self.text = text
        self.mask = mask
        self.width = width + 2
        self.height = height
        self.bg = bg
        self.border_style = border_style

    def paint(self, buffer: Buffer):
        # background
        if self.mask != 0 or self.bg is not None:
            mask = self.mask if self.bg is None else self.mask | Buffer.MASK_BG_CUSTOM
            buffer.draw_attrs_box(self.x, self.y, self.width, self.height, mask)
            if self.bg is not None:
                buffer.draw_bg_colors_box(self.x, self.y, self.width, self.height, *self.bg)

        # TODO: if border is off, visual artifacts appear - Table node should paint its grid
        # top border
        if self.border_style.top:
            buffer.draw_attrs_box(self.x, self.y, self.width, 1, Buffer.MASK_OVERLINE)

        # left border
        for j in range(self.height):
            buffer.draw_text(self.x, self.y + j, LEFT_BORDER)

        buffer.draw_text(self.x + 1, self.y, self.text)


class HeaderNode(TextCell):
    def __init__(self, key, is_uniform):
        super().__init__(str(key), self.attr_for(is_uniform), AnsiToolkit.instance.style.header)

    # TODO
    def compute_widths(self) -> List[int]:
        self.compute_width()
        return [self.width]

    # TODO
    def set_min_widths(self, sizes: List[int]):
        pass

    @staticmethod
    def attr_for(is_uniform):
        if is_uniform:
            return Buffer.MASK_FG_EMPHASIZED | Buffer.MASK_BG_EMPHASIZED | Buffer.MASK_BOLD
        else:
            return Buffer.MASK_FG_EMPHASIZED | Buffer.MASK_BG_EMPHASIZED


class PrimitiveNode(TextCell):
    def __init__(self, j, attrs: ColumnAttrs = None):
        super().__init__(*self.text_and_mask_for(j), AnsiToolkit.instance.style.cell, self.bg_for(j, attrs))

    @staticmethod
    def text_and_mask_for(j):
        primitive_type = type(j)
        if primitive_type is type(None):
            return 'null', Buffer.MASK_ITALIC
        elif primitive_type is bool:
            return str(j).lower(), Buffer.MASK_ITALIC | Buffer.MASK_BOLD
        elif primitive_type is str:
            width, height = geometry(j)
            max_width = AnsiToolkit.instance.primitive_max_width
            # raise ValueError(max_width)
            return j if max_width is None or width <= max_width else '...', Buffer.MASK_NONE
        else:
            return str(j), Buffer.MASK_BOLD

    @staticmethod
    def bg_for(j, attrs: ColumnAttrs = None) -> Optional[Tuple[int, int, int]]:
        string_value = str(j)
        if attrs is None or not attrs.is_colored(string_value):
            return None
        else:
            return hash_to_rgb_dark(attrs.value_hashes.get(string_value) or hash_code(string_value))


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
        debug("consolidate_min_widths", widths1=widths1, widths2=widths2)
        if len(widths1) != len(widths2):
            debug("consolidate_min_widths", container1=container1, container2=container2)
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
        # top border (for the case, when there is no content that paints its border)
        if AnsiToolkit.instance.style.table.top:
            buffer.draw_attrs_box(self.x, self.y, self.width, 1, Buffer.MASK_OVERLINE)

        # left border (in case there is no contents that normally paints the border)
        for j in range(self.height):
            buffer.draw_text(self.x, self.y + j, '▏')


class EntriesNode(CompositeTableNode):
    def __init__(self, entries, descriptor_f, kit, is_uniform):
        super().__init__(
            [
                self.entry_node(key, descriptor_f(key), subj, is_uniform, kit)
                for key, subj in entries
            ]
        )

    @staticmethod
    def entry_node(key, descriptor, subj, is_uniform, kit):
        node = kit.node(subj, descriptor)
        return HBox([
            HeaderNode(key, is_uniform), node
        ])


class ComplexTableNode(CompositeTableNode):
    def __init__(self, body: RegularTable, column_headers, row_headers):
        corner = HeaderNode('#', False)

        column_headers.compute_height()
        column_headers.compute_width()
        row_headers.compute_height()
        row_headers.compute_width()
        body.compute_height()
        body.compute_width()

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


def descriptor_by_path(d: Descriptor, path: Tuple[str]) -> Descriptor:
    for name in path:
        d = d.items()[name]
    return d


def column_headers_node_for_descriptor(descriptor: Descriptor, vertical: bool, leaf_sink: List = None, name=None):
    debug("column_headers_node_for_descriptor")

    leaf_sink = leaf_sink if leaf_sink is not None else []
    if (descriptor.is_dict() or descriptor.is_list()) and descriptor.is_not_empty():
        nodes = [column_headers_node_for_descriptor(d, vertical, leaf_sink, name) for name, d in descriptor.items().items()]
        if name is None:
            return (NestedRowHeaders if vertical else NestedColumnHeaders)(nodes, leaf_sink)
        else:
            return (HBox if vertical else VBox)([
                HeaderNode(name, False), (VBox if vertical else HBox)(nodes)
            ])
    else:
        debug("column_headers_node_for_descriptor", name=name)
        leaf = HeaderNode(name, False)
        leaf_sink.append(leaf)
        return leaf


def row_headers_node_for_paths(j, descriptor):
    leaf_sink = []
    nodes = [
        row_headers_node_for_paths0(jj, descriptor.item, leaf_sink, name)
        for name, jj in descriptor.enumerate_entries(j)
    ]
    return NestedRowHeaders(nodes, leaf_sink)


def row_headers_node_for_paths0(j, descriptor, leaf_sink, name):
    if descriptor.is_uniform() and descriptor.kind == 'list':
        nodes = [
            row_headers_node_for_paths0(jj, descriptor.item, leaf_sink, name)
            for name, jj in descriptor.enumerate_entries(j)
        ]
        return HBox([
            HeaderNode(name, type(name) is int), VBox(nodes)
        ])
    else:
        leaf = HeaderNode(name, type(name) is int)
        leaf_sink.append(leaf)
        return leaf


def row_headers_node_for_descriptor(j, descriptor: Descriptor, leaf_sink: List = None, name=None):
    leaf_sink = leaf_sink if leaf_sink is not None else []
    # if descriptor.is_uniform() and descriptor.is_list():
    if descriptor.is_uniform():
        nodes = [row_headers_node_for_descriptor(jj, descriptor.item, leaf_sink, name) for name, jj in descriptor.enumerate_entries(j)]
        if name is None:
            return NestedRowHeaders(nodes, leaf_sink)
        else:
            return HBox([
                HeaderNode(name, type(name) is int), VBox(nodes)
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

    def compute_width(self):
        super(NestedColumnHeaders, self).compute_width()
        self.set_min_width(self.width)

    def compute_height(self):
        super(NestedColumnHeaders, self).compute_height()
        self.set_min_height(self.height)

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

    def compute_height(self) -> List[int]:
        super(NestedRowHeaders, self).compute_height()
        return [leaf.width for leaf in self.leaves]

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