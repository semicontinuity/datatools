from typing import Dict, List

from datatools.json.coloring import ColumnAttrs
from datatools.json.coloring_hash import hash_to_rgb, hash_code, color_string
from datatools.jt2h.column_renderer import ColumnRenderer
from util.html.elements import td, span


class ColumnRendererColored(ColumnRenderer):

    def __init__(self, column: str, collapsed: bool, data: List[Dict]):
        super().__init__(column, collapsed)
        self.attrs = self.compute_column_attrs(data, column)

    @staticmethod
    def compute_column_attrs(j, column: str) -> ColumnAttrs:
        attr = ColumnAttrs()
        for record in j:
            cell = record.get(column)
            if cell is not None:
                attr.add_value(cell)
        attr.compute_coloring()
        return attr

    def render_cell(self, row: Dict) -> str:
        value = row.get(self.column)
        return td(
            span(value) if value is not None else None,
            style=self.cell_bg_color_style(value)
        )

    def cell_bg_color_style(self, value):
        if value is None or self.attrs is None:
            return None

        string_value = str(value)
        if not self.attrs.is_colored(string_value):
            return None

        return 'background-color: ' + color_string(
            hash_to_rgb(self.attrs.value_hashes.get(string_value) or hash_code(string_value)))