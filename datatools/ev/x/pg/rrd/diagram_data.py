from collections import defaultdict
from typing import Hashable

from datatools.dbview.x.util.qualified_name import QualifiedName
from datatools.ev.x.pg.rrd.card_data import CardData
from datatools.ev.x.pg.rrd.graph_data import GraphData


class DiagramData:

    def __init__(self) -> None:
        self.table_to_pk_value_to_card: dict[dict[str, CardData]] = defaultdict(dict)
        self.generic_edges = set()

    def add_card(self, card_data: CardData):
        if len(card_data.metadata.primaryKeys) != 1:
            raise Exception('Expected 1 pk in ' + card_data.metadata.table)
        if len(card_data.rows) != 1:
            raise Exception('Expected 1 row in result set from ' + str(card_data.metadata.table))
        row = card_data.rows[0]
        pk = card_data.metadata.primaryKeys[0]

        self.table_to_pk_value_to_card[card_data.metadata.table][row[pk]] = card_data

    def add_generic_edge(self, src_table: str, src_column: str, dst_table: str, dst_column: str):
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

    def _record_id(self, table: str, key: Hashable):
        return f'{table}__{hash(key)}'