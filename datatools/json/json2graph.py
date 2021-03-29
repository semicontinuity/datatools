#!/usr/bin/env python3

"""
Utility to convert directed graphs, specified in JSON, to dot format.

Example JSONs:

{"A":["B", "C"]}

{"A":{"B": 2, "C": null}}

[ {"key":["A","X"], "value":[{"key":"B"}] } ]
"""

import json
import sys

from graphviz import Digraph


def label(node):
    if type(node) is tuple or type(node) is list:
        return '|'.join(str(e) for e in node)
    else:
        return str(node)


# perhaps, can also support plain list of edges, like [["A", "B"], ["B", "C"]]
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
    attr = {"node_attr": {'height': '0'}, "graph_attr": {"concentrate": "true"}}

    if type(o) is list:
        return adj_lists_to_graph(o, **attr)
    if type(o) is dict:
        return adj_dict_to_graph(o, **attr)
    else:
        raise ValueError()


if __name__ == "__main__":
    sys.stdout.buffer.write(str(to_graph(json.load(sys.stdin)).source).encode('utf-8'))
