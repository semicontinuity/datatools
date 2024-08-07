#!/usr/bin/env python3
# ======================================================================================================================
# Reads graph from stdin in edge list format
#
# [
#   { "src": "field name", "dst": "field name" },
#   ...
# ]
# ======================================================================================================================

import json
import os
import sys
from collections import defaultdict
from typing import Dict, Iterable, List

from datatools.mini_erd.graph.graph import TableField, Edge, Table
from datatools.mini_erd.graph.graph import Graph
from datatools.mini_erd.ui.focus_table_model import FocusTableModel
from datatools.mini_erd.ui.ui_toolkit import UiToolkit
from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.blocks.vbox import VBox
from datatools.tui.buffer.json2ansi_buffer import Buffer
from datatools.tui.terminal import screen_size_or_default


def paint_erd(table: str, data):
    graph = to_graph(data)
    # focus_graph = filter_graph(table, graph.table_fields[table])
    focus_graph = graph

    focus_table = focus_graph.get_table(table)
    if focus_table is None:
        return

    root = build_ui(focus_table, UiToolkit())
    root.compute_width()
    root.compute_height()
    root.compute_position(0, 0)

    height = root.height
    buffer = Buffer(root.width, height)
    root.paint(buffer)

    screen_width, screen_height = screen_size_or_default()
    buffer.flush(screen_width, height)


def load_data():
    return json.load(sys.stdin)


def to_graph(j) -> Graph:
    graph = Graph()

    for record in j:
        src_field = graph.add_table_field(*record['src'].split(':'))
        dst_field = graph.add_table_field(*record['dst'].split(':'))
        graph.add_edge(src_field, dst_field)

    return graph


# not working?
def filter_graph(focus_table_name: str, focus_table: Dict[str, TableField]) -> Graph:
    graph = Graph()
    graph.add_table(focus_table_name, focus_table)

    for field in focus_table.values():
        for edge in field.outbound.values():
            graph.add_edge(field, graph.add_table_field(edge.dst.table, edge.dst.name))
        for edge in field.inbound.values():
            graph.add_edge(graph.add_table_field(edge.src.table, edge.src.name), field)

    return graph


def build_ui(focus_table: Table, tk: UiToolkit) -> Block:
    m = FocusTableModel(focus_table)

    inbound = inbound_tables_ui(tk, m.inbound_edges_by_table)
    focus = focus_table_ui(focus_table.name, m.inbound_edges_by_table, m.outbound_edges_by_table, m.size_by_outbound_table, tk)
    outbound = outbound_tables_ui(tk, m.outbound_edges_by_table, m.size_by_outbound_table)

    contents = []

    if len(inbound) > 0:
        contents += inbound
        contents += inbound_many_to_one_arrows(tk, m.inbound_edges_by_table)

    contents += focus

    if len(outbound) > 0:
        contents += outbound_many_to_one_arrows(tk, m.outbound_edges_by_table, m.size_by_outbound_table)
        contents += outbound

    return tk.vbox(
        tk.with_spacers_around([tk.hbox(contents)])
    )


def focus_table_ui(focus_table_name, inbound_edges_by_table, outbound_edges_by_table, size_by_outbound_table, tk):
    vbox_elements = [tk.focus_node(focus_table_name)]

    # primary keys (in fact, just one; or may be just one, but without any foreign keys pointing to it)
    field_names = {e.dst.name for table_name, inbound_edges in inbound_edges_by_table.items() for e in inbound_edges}
    for field_name in field_names:
        vbox_elements.append(tk.primary_key_node(field_name))
    # placeholder for primary key
    if len(field_names) == 0:
        vbox_elements.append(tk.text_node(''))

    # separator
    vbox_elements.append(tk.text_node(''))

    # foreign keys
    for table_name, size in size_by_outbound_table.items():
        outbound_edges = outbound_edges_by_table[table_name]
        for e in outbound_edges:
            vbox_elements.append(tk.foreign_key_node(e.src.name))
        for i in range(size - len(outbound_edges) + 2):
            vbox_elements.append(tk.text_node(''))

    return [tk.vbox(vbox_elements)]


def inbound_tables_ui(tk, inbound_edges_by_table: Dict[str, Iterable[Edge]]) -> List[VBox]:
    if len(inbound_edges_by_table) <= 0:
        return []

    vbox_elements = []
    for table_name, edges in inbound_edges_by_table.items():
        vbox_elements.append(tk.table_card(table_name, [e.src.name for e in edges], foreign_keys=True))
    return [tk.vbox(tk.with_spacers_between(vbox_elements))]


def outbound_tables_ui(tk, outbound_edges_by_table: Dict[str, Iterable[Edge]], size_by_outbound_table) -> List[VBox]:
    if len(outbound_edges_by_table) <= 0:
        return []

    vbox_elements = [tk.mini_spacer(0, 2)]
    for table_name, size in size_by_outbound_table.items():
        outbound_edges = outbound_edges_by_table[table_name]
        field_names = {e.dst.name for e in outbound_edges}
        vbox_elements.append(tk.table_card(table_name, field_names, foreign_keys=False))
        for i in range(size - len(field_names) + 1):
            vbox_elements.append(tk.spacer())

    return [
        tk.vbox(vbox_elements)
    ]


def inbound_many_to_one_arrows(tk, inbound_edges_by_table: Dict[str, List[Edge]]) -> List[VBox]:
    inbound_edges_by_table = {k: v for k, v in inbound_edges_by_table.items() if len(v) > 0}
    if len(inbound_edges_by_table) <= 0:
        return []

    vbox_elements = []
    table_index = 0

    for table_name, edges in inbound_edges_by_table.items():

        size = len(edges)

        if table_index > 0:
            vbox_elements.append(tk.text_block(' │'))
        else:
            vbox_elements.append(tk.spacer())

        for i in range(size):
            if i == 0 and table_index == 0 and size == 1 and len(inbound_edges_by_table) == 1:
                vbox_elements.append(tk.text_block('───▶'))
            elif i == 0 and table_index == 0 and size == 1:
                vbox_elements.append(tk.text_block('─┬─▶'))
            elif table_index == len(inbound_edges_by_table) - 1 and i == size - 1:
                vbox_elements.append(tk.text_block('─┘'))
            elif i > 0 or table_index > 0:
                vbox_elements.append(tk.text_block('─┤'))
            else:
                vbox_elements.append(tk.text_block('─┬─▶'))

        if table_index < len(inbound_edges_by_table) - 1:
            vbox_elements.append(tk.text_block(' │'))

        table_index += 1

    return [
        tk.vbox(vbox_elements)
    ]


def outbound_many_to_one_arrows(tk, outbound_edges_by_table: Dict[str, Iterable[Edge]], size_by_outbound_table) -> List[VBox]:
    if len(outbound_edges_by_table) <= 0:
        return []

    vbox_elements = [tk.mini_spacer(0, 2)]
    for table_name, size in size_by_outbound_table.items():
        vbox_elements.append(tk.text_block(''))
        for i in range(size):
            if i == 0:
                vbox_elements.append(tk.text_block('───▶' if size == 1 else '─┬─▶'))
            else:
                vbox_elements.append(tk.text_block('─┘' if i == size - 1 else '─┤'))

        vbox_elements.append(tk.text_block(''))
    vbox_elements.append(tk.text_block(''))

    return [
        tk.vbox(vbox_elements)
    ]


def group_inbound_edges_by_src_table(table_name: str, table: Dict[str, TableField]) -> Dict[str, Iterable[Edge]]:
    result = defaultdict(list)
    for field in table.values():
        for edge in field.inbound.values():
            if edge.src.table != table_name:
                result[edge.src.table].append(edge)
    return result


def group_outbound_edges_by_dst_table(table_name: str, table: Dict[str, TableField]) -> Dict[str, Iterable[Edge]]:
    result = defaultdict(list)
    for field in table.values():
        for edge in field.outbound.values():
            if edge.dst.table != table_name:
                result[edge.dst.table].append(edge)
    return result


if __name__ == "__main__":
    paint_erd(os.environ['TABLE'], load_data())
