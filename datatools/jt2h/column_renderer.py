from typing import Dict


class ColumnRenderer:
    column: str

    def __init__(self, column: str) -> None:
        self.column = column

    def render_cell(self, row: Dict) -> str:
        pass
