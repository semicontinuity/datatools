from collections import defaultdict
from typing import Dict, Iterable

from datatools.mini_erd.graph.graph import Edge, Field


class FocusTableModel:
    inbound_edges_by_table: Dict[str, Iterable[Edge]]
    outbound_edges_by_table: Dict[str, Iterable[Edge]]
    outbound_edges_by_table: Dict[str, int]

    def __init__(
            self,
            focus_table_name: str,
            focus_table: Dict[str, Field],
    ) -> None:
        self.inbound_edges_by_table = group_inbound_edges_by_src_table(focus_table_name, focus_table)
        self.outbound_edges_by_table = group_outbound_edges_by_dst_table(focus_table_name, focus_table)

        # len({e.dst.name for e in outbound_edges}) is always 1
        self.size_by_outbound_table = {
            table_name: max(len({e.src.name for e in outbound_edges}), len({e.dst.name for e in outbound_edges}))
            for table_name, outbound_edges in self.outbound_edges_by_table.items()
        }


def group_inbound_edges_by_src_table(table_name: str, table: Dict[str, Field]) -> Dict[str, Iterable[Edge]]:
    result = defaultdict(list)
    for field in table.values():
        for edge in field.inbound.values():
            if edge.src.table != table_name:
                result[edge.src.table].append(edge)
    return result


def group_outbound_edges_by_dst_table(table_name: str, table: Dict[str, Field]) -> Dict[str, Iterable[Edge]]:
    result = defaultdict(list)
    for field in table.values():
        for edge in field.outbound.values():
            if edge.dst.table != table_name:
                result[edge.dst.table].append(edge)
    return result
