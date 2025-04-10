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
from typing import Hashable

from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.ev.x.pg.rrd.card_data import CardData
from datatools.ev.x.pg.rrd.records_relation_diagram_helper import make_graph, make_subgraph
from datatools.util.dataclasses import dataclass_from_dict


class DiagramData:

    def __init__(self) -> None:
        self.table_to_pk_to_data: dict[dict[str, CardData]] = defaultdict(dict)
        self.table_to_fks = defaultdict(set)
        self.generic_edges = set()

    def _record_id(self, table: str, key: Hashable):
        return f'{table}__{hash(key)}'

    def add(self, card_data: CardData):
        if len(card_data.metadata.primaryKeys) != 1:
            raise Exception('Expected 1 pk in ' + card_data.metadata.table)
        if len(card_data.rows) != 1:
            raise Exception('Expected 1 row in result set from ' + str(card_data.metadata.table))
        row = card_data.rows[0]
        pk = card_data.metadata.primaryKeys[0]

        self.table_to_pk_to_data[card_data.metadata.table][row[pk]] = card_data

    def add_generic_edge(self, src_table: str, src_column: str, dst_table: str, dst_column: str):
        self.table_to_fks[src_table].add(src_column)

        if src_table == dst_table:
            return
        if src_table not in self.table_to_pk_to_data:
            return
        if dst_table not in self.table_to_pk_to_data:
            return

        self.generic_edges.add((src_table, src_column, dst_table, dst_column))

    def make_dot(self):
        dot = make_graph()

        for table, pk_to_data in self.table_to_pk_to_data.items():
            for pk, db_entity_data in pk_to_data.items():
                record_pk = db_entity_data.rows[0][db_entity_data.metadata.primaryKeys[0]]
                dot.subgraph(
                    make_subgraph(
                        db_entity_data,
                        self._record_id(db_entity_data.metadata.table, record_pk),
                        self.table_to_fks[db_entity_data.metadata.table],
                    )
                )

        for src_table, src_column, dst_table, dst_column in self.generic_edges:
            src_table_records: dict[str, DbEntityData] = self.table_to_pk_to_data[src_table]
            dst_table_records: dict[str, DbEntityData] = self.table_to_pk_to_data[dst_table]

            for src_key, db_entity_data in src_table_records.items():
                dst_key = db_entity_data.rows[0][src_column]
                # dst_key must be PK of dst_table
                if dst_key in dst_table_records and dst_table_records[dst_key].rows[0][dst_column] == dst_key:
                    src_id = self._record_id(src_table, src_key)
                    dst_id = self._record_id(dst_table, dst_key)

                    if os.environ.get('RANKDIR') == 'RL':
                        dot.edge(f'{src_id}:{src_column}.l:w', f'{dst_id}')
                    else:
                        dot.edge(f'{src_id}:{src_column}.r:e', f'{dst_id}')

        return dot


def main():
    cards = [dataclass_from_dict(CardData, c) for c in json.load(sys.stdin)]

    diagram_data = make_diagram_data(cards)

    dot = diagram_data.make_dot()
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


if __name__ == '__main__':
    sys.exit(main() or 0)
