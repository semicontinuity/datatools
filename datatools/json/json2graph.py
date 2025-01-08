#!/usr/bin/env python3

"""
Utility to convert directed graphs, specified in JSON, to dot format.

Examples of supported JSONs:

{"A":["B", "C"]}

{"A":{"B": 2, "C": null}}

[ {"key":["A","X"], "value":[{"key":"B"}] } ]

[["A", "B"], ["B", "C"]]

[{"group1": ["a", "b"], "group2": ["c"]}, [["a", "c"], ["b", "c"]]]

"""

import json
import os
import sys
from collections import defaultdict
from typing import List, Set, Dict

from graphviz import Digraph


def label(node):
    if type(node) is tuple or type(node) is list:
        return '|'.join(str(e) for e in node)
    else:
        return str(node)


# List of edges with qualified vertex names, e.g  [["g1.A", "g2.B"], ["g2.B", "g2.C"]] => 2 groups exist, g1 and g2
def qualified_edge_list_to_graph(edges: List, **kwargs):
    groups = defaultdict(set)
    new_edges: List = []
    for edge in edges:
        edge_spec_from = edge[0]
        group_and_node_from = edge_spec_from.split(".")
        if len(group_and_node_from) == 2:
            node_from = group_and_node_from[1]
            groups[group_and_node_from[0]].add(node_from)
        else:
            node_from = edge_spec_from

        edge_spec_to = edge[1]
        group_and_node_to = edge_spec_to.split(".")
        if len(group_and_node_to) == 2:
            node_to = group_and_node_to[1]
            groups[group_and_node_to[0]].add(node_to)
        else:
            node_to = edge_spec_to

        new_edges.append([node_from, node_to])

    return group_specs_and_edge_list_to_graph(groups, new_edges, **kwargs)


def group_specs_and_edge_list_to_graph(groups: Dict, edges: List, **kwargs):
    g = Digraph(**kwargs)
    for group_name, group_nodes in groups.items():
        with g.subgraph(name='cluster_' + group_name) as c:
            c.attr(label=group_name)
            for node in group_nodes:
                c.node(node)

    add_edge_list_to_graph(edges, g)
    return g


def edge_list_to_graph(edges, **kwargs):
    g = Digraph(**kwargs)
    add_nodes_from_edges(edges, g)
    add_edge_list_to_graph(edges, g)
    return g


def add_nodes_from_edges(edges, g):
    nodes: Set[str] = set()
    for edge in edges:
        node_1 = edge[0]
        node_2 = edge[1]
        nodes.add(node_1)
        nodes.add(node_2)
    for node in nodes:
        g.node(str(node), label(node))


def add_edge_list_to_graph(edges, g):
    for edge in edges:
        g.edge(str(edge[0]), str(edge[1]))


def adj_lists_to_graph(adj_list_records, **kwargs):
    g = Digraph(**kwargs)

    for record in adj_list_records:
        node = record['key']
        g.node(str(node), label(node))

    for record in adj_list_records:
        node = record['key']
        adj = record['value']
        for target_record in adj:
            target = target_record['key']
            g.edge(str(node), str(target))

    return g


def adj_dict_to_graph(d, **kwargs):
    g = Digraph(**kwargs)

    for node in d:
        g.node(str(node), label(node))

    for node, adj in d.items():
        if type(adj) is list:
            for target_node in adj:
                g.edge(str(node), str(target_node))
        elif type(adj) is dict:
            for target_node, value in adj.items():
                g.edge(str(node), str(target_node), None if value is None else str(value))
        elif type(adj) is str:
            g.edge(str(node), str(adj))
        elif adj is None:
            pass
        else:
            raise ValueError

    return g


def to_graph(o):
    attr = {
        "node_attr": {'height': '0'},
        "graph_attr": {"concentrate": "true"}
    }
    if type(o) is list:
        records: List = o
        if len(records) == 2 and type(records[0]) is dict and type(records[1]) is list:
            # Group specs + Edge list, e.g. [{"group1": ["a", "b"], "group2": ["c"]}, [["a", "c"], ["b", "c"]]]
            return group_specs_and_edge_list_to_graph(records[0], records[1], **attr)
        elif type(records[0]) is list:
            if len(records) == 2 and type(records[0]) is dict and type(records[1]) is list:
                # Group specs + Edge list, e.g. [{"group1": ["a", "b"], "group2": ["c"]}, [["a", "c"], ["b", "c"]]]
                return group_specs_and_edge_list_to_graph(records[0], records[1], **attr)
            else:
                # List of edges, e.g  [["A", "B"], ["B", "C"]]
                # return edge_list_to_graph(records, **attr)
                return qualified_edge_list_to_graph(records, **attr)
        else:
            # [ {"key":["A","X"], "value":[{"key":"B"}] } ]
            return adj_lists_to_graph(o, **attr)
    if type(o) is dict:
        return adj_dict_to_graph(o, **attr)
    else:
        raise ValueError()


if __name__ == "__main__":
    graph = to_graph(json.load(sys.stdin))
    if os.environ.get('LR'):
        graph.graph_attr['rankdir'] = 'LR'
    sys.stdout.buffer.write(str(graph.source).encode('utf-8'))
