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

from datatools.mini_erd.graph.field import Field
from datatools.mini_erd.graph.graph import Graph
from datatools.mini_erd.ui_toolkit import UiToolkit
from datatools.tui.buffer.blocks.block import Block
from datatools.tui.buffer.json2ansi_buffer import Buffer
from datatools.tui.terminal import screen_size_or_default


def main(table: str, data):
    graph = to_graph(data)

    focus_graph = filter_graph(graph.fields[table])

    root = build_ui(focus_graph.fields[table], UiToolkit())
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
        src_field = graph.add_field(record['src'])
        dst_field = graph.add_field(record['dst'])
        graph.add_edge(src_field, dst_field)

    return graph


def filter_graph(focus: Field) -> Graph:
    graph = Graph()
    focus_field = graph.add_field(focus.name)
    for edge in focus.outbound.values():
        graph.add_edge(focus_field, graph.add_field(edge.dst.name))

    for edge in focus.inbound.values():
        graph.add_edge(graph.add_field(edge.src.name), focus_field)

    return graph


def build_ui(focus: Field, tk: UiToolkit) -> Block:
    elements = []

    if len(focus.inbound) > 0:
        vbox_elements = []
        for edge in focus.inbound.values():
            vbox_elements.append(tk.header_node(edge.src.name))
        elements.append(tk.vbox(vbox_elements))

    elements.append(tk.focus_node(focus.name))

    if len(focus.outbound) > 0:
        vbox_elements = []
        for edge in focus.outbound.values():
            vbox_elements.append(tk.header_node(edge.dst.name))
        elements.append(tk.vbox(vbox_elements))

    return tk.hbox(tk.with_spacers_between(elements))


if __name__ == "__main__":
    main(os.environ['TABLE'], load_data())
