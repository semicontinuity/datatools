"""
Utility to convert directed graphs, specified in JSON, to dot format.

Example JSONs:

{"A":["B", "C"]}

{"A":{"B": 2, "C": null}}

[ {"key":["A","X"], "value":[{"key":"B"}] } ]
"""

import sys
import json
from graphviz import Digraph, Graph


def label(node):
    if type(node) is tuple or type(node) is list:
        return '|'.join(str(e) for e in node)
    else:
        return str(node)


# perhaps, can also support plain list of edges, like [["A", "B"], ["B", "C"]]
def adj_lists_to_graph(l):
    g = Digraph(node_attr={'shape': 'record'}, graph_attr={"concentrate": "true"})

    for record in l:
        node = record['key']
        g.node(str(node), label(node))

    for record in l:
        node = record['key']
        adj = record['value']
        for target_record in adj:
            target = target_record['key']
            g.edge(str(node), str(target))

    return g


def adj_dict_to_graph(d):
    g = Digraph(graph_attr={"concentrate": "true"})
    g.attr('node', shape='box', style='filled', color='wheat')

    for node in d:
        g.node(str(node), label(node))

    for node, adj in d.items():
        if type(adj) is list:
            for target_node in adj:
                g.edge(str(node), str(target_node))
        elif type(adj) is dict:
            for target_node, value in adj.items():
                g.edge(str(node), str(target_node), None if value is None else str(value))
        else:
            raise ValueError

    return g


def to_graph(o):
    if type(o) is list:
        return adj_lists_to_graph(o)
    if type(o) is dict:
        return adj_dict_to_graph(o)
    else:
        raise ValueError()


if __name__ == "__main__":
    sys.stdout.buffer.write(to_graph(json.load(sys.stdin)).pipe(format='dot'))
