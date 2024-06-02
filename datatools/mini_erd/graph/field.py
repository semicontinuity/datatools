from typing import Dict

from datatools.mini_erd.graph.edge import Edge


class Field:
    name: str
    inbound: Dict[str, Edge]
    outbound: Dict[str, Edge]

    def __init__(self, name: str) -> None:
        self.name = name
        self.inbound = {}
        self.outbound = {}

    def __repr__(self) -> str:
        return self.name

