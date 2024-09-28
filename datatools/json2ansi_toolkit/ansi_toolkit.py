from typing import Dict, Hashable, List

from datatools.json.coloring import ColumnAttrs, compute_column_attrs
from datatools.json.coloring_cross_column import compute_cross_column_attrs
from datatools.json.structure_discovery import Discovery, Descriptor, AnyDescriptor, MappingDescriptor, \
    compute_column_paths, descriptor_by_path, child_by_path, compute_row_paths
from datatools.json2ansi_toolkit.complex_table_node import ComplexTableNode
from datatools.json2ansi_toolkit.entries_node import EntriesNode
from datatools.json2ansi_toolkit.header_node import HeaderNode
from datatools.json2ansi_toolkit.nested_column_headers import NestedColumnHeaders
from datatools.json2ansi_toolkit.nested_row_headers import NestedRowHeaders
from datatools.json2ansi_toolkit.page_node import PageNode
from datatools.json2ansi_toolkit.primitive_node import PrimitiveNode
from datatools.json2ansi_toolkit.style import Style
from datatools.json2ansi_toolkit.ui_factory import UiFactory
from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.blocks.hbox import HBox
from datatools.tui.buffer.blocks.regular_table import RegularTable
from datatools.tui.buffer.blocks.vbox import VBox
from datatools.util.logging import debug, stderr_print
from datatools.util.text_util import geometry


class AnsiToolkit(UiFactory):
    instance: 'AnsiToolkit'
    discovery: Discovery
    style: Style

    def __init__(self, discovery, style: Style, primitive_max_width=64):
        self.discovery = discovery
        self.style = style
        self.primitive_max_width = primitive_max_width
        AnsiToolkit.instance = self

    def header_node(self, text, is_uniform):
        return HeaderNode(text, is_uniform, self.style.header)

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
        return PrimitiveNode('', AnsiToolkit.instance.style.cell)

    def primitive(self, j, attrs: ColumnAttrs = None):
        if type(j) is str and AnsiToolkit.instance.primitive_max_width is not None:
            width, height = geometry(j)
            if width > AnsiToolkit.instance.primitive_max_width:
                j = '...'
        return PrimitiveNode(j, AnsiToolkit.instance.style.cell, attrs)

    def list_of_single_record(self, element, element_descriptor):
        return HBox([
            HeaderNode('0', True, self.style.header),
            self.object_node(element.items(), element_descriptor.entry)
        ])

    def list_of_multi_record(self, j, descriptor):
        return EntriesNode(enumerate(j), descriptor.entry, self, True, self.style.table)

    def array(self, j, descriptor):
        return EntriesNode(enumerate(j), lambda key: descriptor.item, self, len(j) > 1, self.style.table) # hack

    def object_node(self, items, descriptor_f):
        return EntriesNode(items, descriptor_f, self, False, self.style.table)

    def matrix_node(self, j, descriptor):
        return self.array(j, descriptor)

    def uniform_table_node(self, j, descriptor: MappingDescriptor):
        debug("uniform_table_node")
        item_descriptor = descriptor.item
        # column_headers = HBox([HeaderNode(column_name, False) for column_name in item_descriptor.dict])
        # body = RegularTable([
        #     HBox([self.node(entry[col_name], col_desc) for col_name, col_desc in item_descriptor.dict.items()])
        #     for i, entry in enumerate(j)
        # ])

        row_headers = VBox([HeaderNode(k, True, self.style.header) for k, v in descriptor.enumerate_entries(j)])
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

        return ComplexTableNode(body, column_headers, row_headers, self.style.table, HeaderNode('#', False, AnsiToolkit.instance.style.header))

    def uniform_table_node2(self, j, descriptor: MappingDescriptor):
        debug("uniform_table_node2", descriptor=type(descriptor))
        row_paths, generic_row_descriptor = compute_row_paths(j, descriptor)
        debug("uniform_table_node2", row_paths=row_paths, generic_row_descriptor=generic_row_descriptor)
        # item_descriptor = descriptor.inner_item()
        # item_descriptor = descriptor.item
        item_descriptor = generic_row_descriptor
        debug("uniform_table_node2", item_descriptor=item_descriptor)
        column_paths = compute_column_paths(item_descriptor)
        debug("uniform_table_node2", column_paths=column_paths)

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

        return ComplexTableNode(body, column_headers, row_headers, self.style.table, HeaderNode('#', False, AnsiToolkit.instance.style.header))

    def uniform_table_node2_tr(self, row, row_descriptor, column_paths, column_id_to_attrs):
        debug("uniform_table_node2_tr", row_descriptor=row_descriptor)
        return HBox([
            self.uniform_table_cell_node(row, row_descriptor, path, column_id_to_attrs.get(path))
            for path in column_paths
        ])

    def uniform_table_cell_node(self, row, item_descriptor, path, attrs: ColumnAttrs = None):
        child = child_by_path(row, path)
        debug("uniform_table_cell_node", path=path, child=child)
        if child is ...:
            return self.empty()
        else:
            # self.discovery.
            d = descriptor_by_path(item_descriptor, path)
            # debug("uniform_table_cell_node", d=d)
            if d.is_primitive():
                return self.primitive(child, attrs)
            else:
                # return self.node(child, d)
                return self.block(child)


def column_headers_node_for_descriptor(descriptor: Descriptor, vertical: bool, leaf_sink: List = None, name=None):
    debug("column_headers_node_for_descriptor")

    leaf_sink = leaf_sink if leaf_sink is not None else []
    if (descriptor.is_dict() or descriptor.is_list()) and descriptor.is_not_empty():
        nodes = [column_headers_node_for_descriptor(d, vertical, leaf_sink, name) for name, d in descriptor.items().items()]
        if name is None:
            return (NestedRowHeaders if vertical else NestedColumnHeaders)(nodes, leaf_sink)
        else:
            return (HBox if vertical else VBox)([
                HeaderNode(name, False, AnsiToolkit.instance.style.header), (VBox if vertical else HBox)(nodes)
            ])
    else:
        debug("column_headers_node_for_descriptor", name=name)
        leaf = HeaderNode(name, False, AnsiToolkit.instance.style.header)
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
            HeaderNode(name, type(name) is int, AnsiToolkit.instance.style.header), VBox(nodes)
        ])
    else:
        leaf = HeaderNode(name, type(name) is int, AnsiToolkit.instance.style.header)
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
                HeaderNode(name, type(name) is int, AnsiToolkit.instance.style.header), VBox(nodes)
            ])
    else:
        leaf = HeaderNode(name, type(name) is int, AnsiToolkit.instance.style.header)
        leaf_sink.append(leaf)
        return leaf
