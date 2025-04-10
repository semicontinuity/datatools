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
from collections import defaultdict
from dataclasses import astuple
from typing import Hashable

from datatools.dbview.x.util.qualified_name import QualifiedName
from datatools.ev.x.pg.rrd.card_data import CardData
from datatools.ev.x.pg.rrd.graph_data import GraphData
from datatools.ev.x.pg.rrd.records_relation_diagram_helper import make_graph, make_subgraph_with_node, \
    render_table_record_as_label
from datatools.util.dataclasses import dataclass_from_dict


def main():
    cards = [dataclass_from_dict(CardData, c) for c in json.load(sys.stdin)]

    diagram_data = make_diagram_data(cards)

    dot = diagram_data.make_dot(diagram_data.to_graph_data())
    if os.environ.get('SVG'):
        sys.stdout.buffer.write(dot.pipe(format='svg'))
    else:
        print(dot.source)


def make_diagram_data(cards):
    diagram_data = DiagramData()

    for card in cards:
        diagram_data.add(card)

        for r in card.metadata.relations:
            src_table = r.src.qualifier
            src_column = r.src.name
            dst_table = r.dst.qualifier
            dst_column = r.dst.name
            diagram_data.add_generic_edge(src_table, src_column, dst_table, dst_column)

    return diagram_data


class DiagramData:

    def __init__(self) -> None:
        self.table_to_pk_value_to_card: dict[dict[str, CardData]] = defaultdict(dict)
        self.table_fk_names = defaultdict(set)
        self.generic_edges = set()

    def add(self, card_data: CardData):
        if len(card_data.metadata.primaryKeys) != 1:
            raise Exception('Expected 1 pk in ' + card_data.metadata.table)
        if len(card_data.rows) != 1:
            raise Exception('Expected 1 row in result set from ' + str(card_data.metadata.table))
        row = card_data.rows[0]
        pk = card_data.metadata.primaryKeys[0]

        self.table_to_pk_value_to_card[card_data.metadata.table][row[pk]] = card_data

    def add_generic_edge(self, src_table: str, src_column: str, dst_table: str, dst_column: str):
        self.table_fk_names[src_table].add(src_column)

        if src_table == dst_table:
            return
        if src_table not in self.table_to_pk_value_to_card:
            return
        if dst_table not in self.table_to_pk_value_to_card:
            return

        self.generic_edges.add((src_table, src_column, dst_table, dst_column))

    def to_graph_data(self) -> GraphData:
        return GraphData(self._nodes(), self._edges())

    def _nodes(self):
        nodes: dict[str, CardData] = {}
        for table, pk_value_to_card in self.table_to_pk_value_to_card.items():
            for pk_value, card_data in pk_value_to_card.items():
                nodes[self._record_id(card_data.metadata.table, pk_value)] = card_data
        return nodes

    def _edges(self):
        edges: list[tuple[QualifiedName, QualifiedName]] = []
        # match generic edges against cards
        for src_table, src_column, dst_table, dst_column in self.generic_edges:
            src_table_records: dict[str, CardData] = self.table_to_pk_value_to_card[src_table]
            dst_table_records: dict[str, CardData] = self.table_to_pk_value_to_card[dst_table]

            for src_fk_value, card_data in src_table_records.items():
                dst_pk_value = card_data.rows[0][src_column]
                # dst_pk_value must be PK of dst_table
                if dst_pk_value in dst_table_records and dst_table_records[dst_pk_value].rows[0][
                    dst_column] == dst_pk_value:
                    src_id = self._record_id(src_table, src_fk_value)
                    dst_id = self._record_id(dst_table, dst_pk_value)
                    edges.append((QualifiedName(src_id, src_column), QualifiedName(dst_id, dst_column)))
        return edges

    def make_dot(self, g: GraphData):
        dot = make_graph()

        for node_id, card_data in g.nodes.items():
            dot.subgraph(
                make_subgraph_with_node(
                    node_id,
                    node_label=render_table_record_as_label(
                        row=card_data.rows[0],
                        table_name=card_data.metadata.table,
                        pk_names=card_data.metadata.primaryKeys,
                        fk_names=self.table_fk_names[card_data.metadata.table]
                    )
                )
            )

        for src, dst in g.edges:
            src_id, src_column = astuple(src)
            dst_id, dst_column = astuple(dst)
            src_suffix = 'l:w' if os.environ.get('RANKDIR') == 'RL' else 'r:e'
            dot.edge(f'{src_id}:{src_column}.{src_suffix}', f'{dst_id}')

        return dot

    def _record_id(self, table: str, key: Hashable):
        return f'{table}__{hash(key)}'


if __name__ == '__main__':
    sys.exit(main() or 0)
