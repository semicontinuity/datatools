from dataclasses import dataclass


@dataclass
class TreeGridContext:
    x: int
    y: int
    width: int
    height: int
    interactive: bool = True