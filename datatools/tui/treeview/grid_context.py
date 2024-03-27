from dataclasses import dataclass


@dataclass
class GridContext:
    x: int
    y: int
    width: int
    height: int
    interactive: bool = True
