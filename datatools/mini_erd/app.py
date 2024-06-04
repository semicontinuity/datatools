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
from typing import Dict

from datatools.mini_erd.graph.graph import Field
from datatools.mini_erd.graph.graph import Graph
from datatools.mini_erd.ui_toolkit import UiToolkit
from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.json2ansi_buffer import Buffer
from datatools.tui.terminal import screen_size_or_default


def paint_erd(table: str, data):
    graph = to_graph(data)
    # focus_graph = filter_graph(table, graph.table_fields[table])
    focus_graph = graph

    root = build_ui(table, focus_graph, UiToolkit())
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


def build_ui(focus_table_name: str, graph: Graph, tk: UiToolkit) -> Block:
    focus_table = graph.table_fields[focus_table_name]
    hbox_elements = []

    inbound_table_names = collect_inbound_table_names(focus_table)
    if len(inbound_table_names) > 0:
        vbox_elements = []
        for name in inbound_table_names:
            vbox_elements.append(table_card(name, tk))
        hbox_elements.append(
            tk.vbox(
                vbox_elements
            )
        )

    hbox_elements.append(
        tk.vbox(
            [
                tk.focus_node(focus_table_name),
            ]
        )
    )

    outbound_table_names = collect_outbound_table_names(focus_table)
    if len(outbound_table_names) > 0:
        vbox_elements = []
        for name in outbound_table_names:
            vbox_elements.append(table_card(name, tk))
        hbox_elements.append(
            tk.vbox(
                vbox_elements
            )
        )

    return tk.hbox(tk.with_spacers_between(hbox_elements))


def table_card(table_name, tk):
    return tk.vbox(
        [
            tk.header_node(table_name)
        ]
    )


def collect_outbound_table_names(table: Dict[str, Field]):
    result = set()
    for field in table.values():
        for edge in field.outbound.values():
            result.add(edge.dst.table)
    return result


def collect_inbound_table_names(table: Dict[str, Field]):
    result = set()
    for field in table.values():
        for edge in field.inbound.values():
            result.add(edge.src.table)
    return result


if __name__ == "__main__":
    paint_erd(os.environ['TABLE'], load_data())
