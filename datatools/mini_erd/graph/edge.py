from dataclasses import dataclass, Field


@dataclass
class Edge:
    src: Field
    dst: Field
