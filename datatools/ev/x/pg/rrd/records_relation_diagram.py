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
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Hashable

from x.util.pg import connect_to_db

from datatools.dbview.x.util.pg_query import query_from_yaml
from datatools.ev.x.pg.db_entity_data import DbEntityData
from datatools.ev.x.pg.pg_data_source import PgDataSource
from datatools.ev.x.pg.realm_pg import RealmPg
from datatools.ev.x.pg.rrd.model import CardData
from datatools.dbview.x.util.result_set_metadata import ResultSetMetadata
from datatools.ev.x.pg.rrd.records_relation_diagram_helper import make_graph, make_subgraph
from datatools.util.dataclasses import dataclass_from_dict


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


def rows_from_jsonl(s: str):
    return [json.loads(row) for row in s.split('\n') if row != '']


def main():
    data_source = PgDataSource(os.environ)
    realm = RealmPg(None, data_source)

    diagram_data = DiagramData()
    tables = set()

    with connect_to_db() as conn:

        folder = Path(os.environ['PWD'])

        all_edges = set()

        for file in folder.rglob('.query'):
            folder = file.parent

            query = query_from_yaml((folder / '.query').read_text(encoding='utf-8'))
            rs_metadata: ResultSetMetadata = dataclass_from_dict(ResultSetMetadata, json.loads((folder / 'rs-metadata.json').read_text(encoding='utf-8')))
            content = rows_from_jsonl((folder / 'content.jsonl').read_text(encoding='utf-8'))

            tables.add(query.table)

            card_data = CardData(
                query.table,
                rs_metadata.primaryKeys,
                content
            )

            diagram_data.add(card_data)

            for r in rs_metadata.relations:
                all_edges.add((r.src, r.dst))

        if len(tables) == 0:
            return 1

        for src, dst in all_edges:
            src_table = src.qualifier
            src_column = src.name
            dst_table = dst.qualifier
            dst_column = dst.name

            diagram_data.add_generic_edge(src_table, src_column, dst_table, dst_column)

    dot = diagram_data.make_dot()
    if os.environ.get('SVG'):
        sys.stdout.buffer.write(dot.pipe(format='svg'))
    else:
        print(dot.source)


if __name__ == '__main__':
    sys.exit(main() or 0)
