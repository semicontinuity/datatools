from dataclasses import dataclass


@dataclass
class ColumnState:
    collapsed: bool = False
