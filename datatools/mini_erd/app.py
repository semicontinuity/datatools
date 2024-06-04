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

from datatools.mini_erd.graph.graph import Field, Edge
from datatools.mini_erd.graph.graph import Graph
from datatools.mini_erd.ui_toolkit import UiToolkit
from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.blocks.vbox import VBox
from datatools.tui.buffer.json2ansi_buffer import Buffer
from datatools.tui.terminal import screen_size_or_default


def paint_erd(table: str, data):
    graph = to_graph(data)
    # focus_graph = filter_graph(table, graph.table_fields[table])
    focus_graph = graph

    focus_table = focus_graph.table_fields.get(table)
    if focus_table is None:
        return

    root = build_ui(table, focus_table, UiToolkit())
    root.compute_width()
    root.compute_height()
    root.compute_position(0, 0)

    buffer = Buffer(root.width, root.height)
    root.paint(buffer)

    screen_size = screen_size_or_default()
    buffer.flush(*screen_size)


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
def filter_graph(focus_table_name: str, focus_table: Dict[str, Field]) -> Graph:
    graph = Graph()
    graph.add_table(focus_table_name, focus_table)

    for field in focus_table.values():
        for edge in field.outbound.values():
            graph.add_edge(field, graph.add_table_field(edge.dst.table, edge.dst.name))
        for edge in field.inbound.values():
            graph.add_edge(graph.add_table_field(edge.src.table, edge.src.name), field)

    return graph


def build_ui(focus_table_name: str, focus_table: Dict[str, Field], tk: UiToolkit) -> Block:
    outbound_edges_by_table = group_outbound_edges_by_dst_table(focus_table_name, focus_table)
    inbound_edges_by_table = group_inbound_edges_by_src_table(focus_table_name, focus_table)

    return tk.vbox(
        tk.with_spacers_around(
            [
                tk.hbox(
                    tk.with_spacers_between(
                        inbound_tables_ui(tk, inbound_edges_by_table) +
                        focus_table_ui(focus_table_name, inbound_edges_by_table, outbound_edges_by_table, tk) +
                        outbound_tables_ui(tk, outbound_edges_by_table)
                    )
                )
            ]
        )
    )


def focus_table_ui(focus_table_name, inbound_edges_by_table, outbound_edges_by_table, tk):
    center_elements = [tk.focus_node(focus_table_name)]
    field_names = {e.dst.name for table_name, inbound_edges in inbound_edges_by_table.items() for e in inbound_edges}
    for field_name in field_names:
        center_elements.append(tk.key_node(field_name, foreign=False))
    center_elements.append(tk.text_node(''))
    for table_name, outbound_edges in outbound_edges_by_table.items():
        for e in outbound_edges:
            center_elements.append(tk.key_node(e.src.name, foreign=True))
        center_elements.append(tk.text_node(''))
    return [tk.vbox(center_elements)]


def inbound_tables_ui(tk, inbound_edges_by_table: Dict[str, Iterable[Edge]]) -> List[VBox]:
    if len(inbound_edges_by_table) <= 0:
        return []

    vbox_elements = []
    for table_name, edges in inbound_edges_by_table.items():
        vbox_elements.append(tk.table_card(table_name, [e.src.name for e in edges], foreign_keys=True))
    return [tk.vbox(tk.with_spacers_between(vbox_elements))]


def outbound_tables_ui(tk, outbound_edges_by_table: Dict[str, Iterable[Edge]]) -> List[VBox]:
    if len(outbound_edges_by_table) <= 0:
        return []

    vbox_elements = []
    for table_name, outbound_edges in outbound_edges_by_table.items():
        field_names = {e.dst.name for e in outbound_edges}
        vbox_elements.append(tk.table_card(table_name, field_names, foreign_keys=False))
    return [tk.vbox(tk.with_spacers_between(vbox_elements))]


def group_inbound_edges_by_src_table(table_name: str, table: Dict[str, Field]) -> Dict[str, Iterable[Edge]]:
    result = defaultdict(list)
    for field in table.values():
        for edge in field.inbound.values():
            if edge.src.table != table_name:
                result[edge.src.table].append(edge)
    return result


def group_outbound_edges_by_dst_table(table_name: str, table: Dict[str, Field]) -> Dict[str, Iterable[Edge]]:
    result = defaultdict(list)
    for field in table.values():
        for edge in field.outbound.values():
            if edge.dst.table != table_name:
                result[edge.dst.table].append(edge)
    return result


if __name__ == "__main__":
    paint_erd(os.environ['TABLE'], load_data())
