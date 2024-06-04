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
from typing import Dict, Iterable

from datatools.mini_erd.graph.graph import Field, Edge
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

    outbound_edges_by_table = group_outbound_edges_by_dst_table(focus_table)

    inbound_cards = collect_inbound_cards(focus_table)
    if len(inbound_cards) > 0:
        vbox_elements = []
        for table_name, field_names in inbound_cards.items():
            vbox_elements.append(tk.table_card(table_name, field_names, foreign_keys=True))
        hbox_elements.append(
            tk.vbox(
                tk.with_spacers_between(
                    vbox_elements
                )
            )
        )

    center_elements = [tk.focus_node(focus_table_name)]
    for table_name, outbound_edges in outbound_edges_by_table.items():
        for e in outbound_edges:
            center_elements.append(tk.key_node(e.src.name, foreign=True))
        center_elements.append(tk.text_node(''))
    hbox_elements.append(tk.vbox(center_elements))

    if len(outbound_edges_by_table) > 0:
        vbox_elements = []
        for table_name, outbound_edges in outbound_edges_by_table.items():
            field_names = {e.dst.name for e in outbound_edges}
            vbox_elements.append(tk.table_card(table_name, field_names, foreign_keys=False))
        hbox_elements.append(
            tk.vbox(
                tk.with_spacers_between(
                    vbox_elements
                )
            )
        )

    return tk.vbox(
        tk.with_spacers_around(
            [tk.hbox(tk.with_spacers_between(hbox_elements))]
        )
    )


def group_inbound_edges_by_src_table(table: Dict[str, Field]) -> Dict[str, Iterable[Edge]]:
    result = defaultdict(list)
    for field in table.values():
        for edge in field.inbound.values():
            result[edge.src.table].append(edge)
    return result


def group_outbound_edges_by_dst_table(table: Dict[str, Field]) -> Dict[str, Iterable[Edge]]:
    result = defaultdict(list)
    for field in table.values():
        for edge in field.outbound.values():
            result[edge.dst.table].append(edge)
    return result


def collect_inbound_cards(table: Dict[str, Field]) -> Dict[str, Iterable[str]]:
    result = defaultdict(set)
    for field in table.values():
        for edge in field.inbound.values():
            result[edge.src.table].add(edge.src.name)
    return result


if __name__ == "__main__":
    paint_erd(os.environ['TABLE'], load_data())
