#!/usr/bin/env python3

######################################################################
# Paints Record Relation Diagram.
# Reads Cards spec in JSON format from STDIN.
#
# Environment vars:
#
# SVG:     generate SVG
# V:       generate verbose diagram (with nulls, INT, BOOL fields)
# RANKDIR: RANKDIR for graph, default LR
######################################################################
import json
import os
import sys

from datatools.ev.x.pg.rrd.card_data import CardData
from datatools.ev.x.pg.rrd.diagram_data import DiagramData
from datatools.ev.x.pg.rrd.dot_renderer import make_dot
from datatools.util.dataclasses import dataclass_from_dict


def main():
    cards = [dataclass_from_dict(CardData, c) for c in json.load(sys.stdin)]

    diagram_data = make_diagram_data(cards)

    dot = make_dot(diagram_data.to_graph_data())
    if os.environ.get('SVG'):
        sys.stdout.buffer.write(dot.pipe(format='svg'))
    else:
        print(dot.source)


def make_diagram_data(cards):
    diagram_data = DiagramData()

    for card in cards:
        diagram_data.add_card(card)

        for r in card.metadata.relations:
            diagram_data.add_generic_edge(r.src.qualifier, r.src.name, r.dst.qualifier, r.dst.name)

    return diagram_data


if __name__ == '__main__':
    sys.exit(main() or 0)
