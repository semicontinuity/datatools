from typing import Dict, List

from datatools.jt2h.column_renderer import ColumnRenderer
from util.html.elements import td, span


class ColumnRendererEntitiesLifecycle(ColumnRenderer):

    def __init__(self, data: List[Dict], column: str):
        super().__init__(column)

    def render_cell(self, row: Dict) -> str:
        return td(
            span('&nbsp;', style='background-color: darkred'),
            span('&nbsp;', style='background-color: darkgreen'),
            span('&nbsp;', style='background-color: darkblue'),
            style='border-top: 0; border-bottom: 0;'
        )
