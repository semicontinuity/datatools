import json
from typing import Dict, List

from datatools.json.coloring import ColumnAttrs
from datatools.json.coloring_hash import hash_to_rgb, hash_code, color_string
from util.html.elements import table, td, tr, thead, tbody, th, span, pre


class Log:

    def __init__(self, j: List[Dict], columns: List) -> None:
        self.columns = columns
        self.j = j
        self.column_attrs: Dict[str, ColumnAttrs] = {
            column: self.compute_column_attrs(j, column) for column in self.columns
        }

    @staticmethod
    def compute_column_attrs(j, column: str) -> ColumnAttrs:
        attr = ColumnAttrs()
        for record in j:
            attr.add_value(record[column])
        attr.compute_coloring()
        return attr

    def cell_bg_color_style(self, column, value):
        attrs = self.column_attrs.get(column)
        if attrs is None:
            return None

        string_value = str(value)
        if not attrs.is_colored(string_value):
            return None

        return 'background-color: ' + color_string(
            hash_to_rgb(attrs.value_hashes.get(string_value) or hash_code(string_value)))

    def __str__(self) -> str:
        return str(
            table(
                thead(
                    th(),
                    (
                        th(column) for column in self.columns
                    )
                ),
                (
                    tbody(
                        tr(
                            th(
                                span('▶', onclick='swapClass(this, "TBODY", "regular", "expanded")', clazz='regular'),
                                span('▼', onclick='swapClass(this, "TBODY", "regular", "expanded")', clazz='expanded')
                            ),
                            (
                                td(row[column], style=self.cell_bg_color_style(column, row[column]))
                                for column in self.columns
                            ),
                        ),
                        tr(
                            th(clazz='details'),
                            td(
                                pre(json.dumps(row, indent=2)),
                                colspan=len(self.columns),
                                clazz='details'
                            )
                        ),
                        clazz='regular'
                    ) for row in self.j
                )
            )
        )
