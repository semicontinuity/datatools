from typing import List, Dict

from datatools.mini_erd.graph.edge import Edge
from datatools.mini_erd.graph.field import Field


class Graph:
    fields: Dict[str, Field]
    edges: List[Edge]

    def __init__(self) -> None:
        self.fields = {}
        self.edges = []

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
