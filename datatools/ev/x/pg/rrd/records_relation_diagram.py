#!/usr/bin/env python3

######################################################################
# Paints Record Relation Diagram.
# Should be launched in 'tables' folder
#
# Environment vars:
#
# SVG:     generate SVG
# V:       generate verbose diagram (with nulls, INT, BOOL fields)
# RANKDIR: RANKDIR for graph, default LR
######################################################################

import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Hashable

from x.util.pg import connect_to_db, get_table_foreign_keys_all_multi

from datatools.dbview.x.util.pg_query import query_from_yaml
from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.realm_pg import RealmPg
from datatools.ev.x.pg.rrd.model import CardData
from datatools.ev.x.pg.rrd.records_relation_diagram_helper import make_graph, make_subgraph


class DiagramData:

    def __init__(self) -> None:
        self.table_to_pk_to_data = defaultdict(dict)
        self.table_to_fks = defaultdict(set)
        self.generic_edges = []

    def _record_id(self, table: str, key: Hashable):
        return f'{table}__{hash(key)}'

    def add(self, card_data: CardData):
        if len(card_data.pks) != 1:
            raise Exception('Expected 1 pk in ' + card_data.table)
        if len(card_data.rows) != 1:
            raise Exception('Expected 1 row in result set from ' + str(card_data.table))
        row = card_data.rows[0]
        pk = card_data.pks[0]

        self.table_to_pk_to_data[card_data.table][row[pk]] = card_data

    def add_generic_edge(self, src_table: str, src_column: str, dst_table: str, dst_column: str):
        self.table_to_fks[src_table].add(src_column)

        if src_table == dst_table:
            return
        if src_table not in self.table_to_pk_to_data:
            return
        if dst_table not in self.table_to_pk_to_data:
            return

        self.generic_edges.append((src_table, src_column, dst_table, dst_column))

    def make_dot(self):
        dot = make_graph()

        for table, pk_to_data in self.table_to_pk_to_data.items():
            for pk, db_entity_data in pk_to_data.items():
                record_pk = db_entity_data.rows[0][db_entity_data.pks[0]]
                dot.subgraph(
                    make_subgraph(
                        db_entity_data,
                        self._record_id(db_entity_data.table, record_pk),
                        self.table_to_fks[db_entity_data.table],
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
    data_source = PgDataSource(os.environ)
    realm = RealmPg(None, data_source)

    diagram_data = DiagramData()
    tables = set()

    with connect_to_db() as conn:

        folder = Path(os.environ['PWD'])
        for file in folder.rglob('.query'):
            query = query_from_yaml(file.read_text(encoding='utf-8'))
            tables.add(query.table)

            entity_data = realm.db_entity_data(conn, query)
            card_data = CardData(entity_data.query.table, entity_data.pks, entity_data.rows)
            # diagram_data.add(entity_data)
            diagram_data.add(card_data)

        if len(tables) == 0:
            return 1

        # could optimize query
        edges = get_table_foreign_keys_all_multi(conn, list(tables))
        for edge in edges:
            src_table = edge['table_name']
            src_column = edge['column_name']
            dst_table = edge['foreign_table_name']
            dst_column = edge['foreign_column_name']
            diagram_data.add_generic_edge(src_table, src_column, dst_table, dst_column)

    dot = diagram_data.make_dot()
    if os.environ.get('SVG'):
        sys.stdout.buffer.write(dot.pipe(format='svg'))
    else:
        print(dot.source)


if __name__ == '__main__':
    sys.exit(main() or 0)
