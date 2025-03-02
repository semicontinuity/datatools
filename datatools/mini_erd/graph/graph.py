from dataclasses import dataclass
from typing import Dict, List, Optional


class TableField:
    name: str
    table: str

    inbound: Dict[str, 'Edge']
    outbound: Dict[str, 'Edge']

    def __init__(self, name: str, table: str = None) -> None:
        self.name = name
        self.table = table
        self.inbound = {}
        self.outbound = {}

    def __repr__(self) -> str:
        return str(self.table) + ':' + self.name


@dataclass
class Edge:
    src: TableField
    dst: TableField


@dataclass
class Table:
    name: str
    fields: Dict[str, TableField]


class Graph:
    table_to_fields_dict: Dict[str, Dict[str, TableField]]
    edges: List[Edge]

    def __init__(self) -> None:
        self.table_to_fields_dict = {}
        self.edges = []

    # def add_table(self, table: Table) -> Dict[str, TableField]:
    def add_table(self, table_name: str, table_fields: Dict[str, TableField]) -> Dict[str, TableField]:
        for field in TreeGrid.values():
            self.add_table_field(table_name, field.name)
        return self.table_to_fields_dict[table_name]

    def add_table_field(self, table_name: str, field_name: str) -> TableField:
        table = self.table_to_fields_dict.get(table_name)
        if table is None:
            table = {}
            self.table_to_fields_dict[table_name] = table

        field = table.get(field_name)
        if field is None:
            field = TableField(field_name, table_name)
            table[field_name] = field

        return field

    def add_edge(self, src: TableField, dst: TableField) -> Edge:
        edge = Edge(src, dst)
        self.edges.append(edge)
        src.outbound[repr(dst)] = edge
        dst.inbound[repr(src)] = edge
        return edge

    def get_table(self, table_name: str) -> Optional[Table]:
        contents = self.table_to_fields_dict.get(table_name)
        if contents is None:
            return None
        else:
            return Table(table_name, contents)
