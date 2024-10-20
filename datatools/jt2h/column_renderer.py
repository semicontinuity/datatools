from typing import Dict


class ColumnRenderer:
    column: str
    collapsed: bool

    def __init__(self, column: str, collapsed: bool) -> None:
        self.column = column
        self.collapsed = collapsed

    def render_cell(self, row: Dict) -> str:
        pass
