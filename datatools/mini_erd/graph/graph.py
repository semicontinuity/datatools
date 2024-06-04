from dataclasses import dataclass
from typing import Dict, List


class Field:
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
    src: Field
    dst: Field


class Graph:
    fields: Dict[str, Field]
    table_fields: Dict[str, Dict[str, Field]]
    edges: List[Edge]

    def __init__(self) -> None:
        self.fields = {}
        self.table_fields = {}
        self.edges = []

    def add_table(self, table_name: str, table_fields: Dict[str, Field]) -> Dict[str, Field]:
        for field in table_fields.values():
            self.add_table_field(table_name, field.name)
        return self.table_fields[table_name]

    def add_table_field(self, table_name: str, field_name: str) -> Field:
        table = self.table_fields.get(table_name)
        if table is None:
            table = {}
            self.table_fields[table_name] = table

        field = table.get(field_name)
        if field is None:
            field = Field(field_name, table_name)
            table[field_name] = field

        return field

    def add_field(self, field_name: str) -> Field:
        field = self.fields.get(field_name)
        if field is None:
            field = Field(field_name)
            self.fields[field_name] = field
        return field

    def add_edge(self, src: Field, dst: Field) -> Edge:
        edge = Edge(src, dst)
        self.edges.append(edge)
        src.outbound[dst.name] = edge
        dst.inbound[src.name] = edge
        return edge
