from typing import Dict, Callable

from datatools.jt2h.column_renderer import ColumnRenderer
from util.html.elements import td


class ColumnRendererCustom(ColumnRenderer):

    def __init__(
            self,
            column: str,
            collapsed: bool,
            text_f: Callable[[Dict], str]
    ):
        super().__init__(column, collapsed)
        self.text_f = text_f

    def render_cell(self, row: Dict) -> str:
        return td(
            self.text_f(row)
        )
