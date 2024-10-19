from typing import Dict, List

from datatools.jt2h.column_renderer import ColumnRenderer
from datatools.jt2h.json_node import JsonNode
from util.html.elements import table, td, tr, thead, tbody, th, span


class Log:

    def __init__(self, j: List[Dict], column_renderers: List[ColumnRenderer]) -> None:
        self.j = j
        self.column_renderers = column_renderers

    def __str__(self) -> str:
        t = table(
            thead(
                th(),
                (
                    th(
                        span(column_renderer.column, clazz='regular'),
                        span(column_renderer.column[:1] + '.', clazz='compact'),
                        onclick=f'toggleParentClass(this, "TABLE", "hide-c-{i + 2}")'
                    )
                    for i, column_renderer in enumerate(self.column_renderers)
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
                            column_renderer.render_cell(row)
                            for column_renderer in self.column_renderers
                        ),
                    ),
                    tr(
                        th(clazz='details'),
                        td(
                            JsonNode(row),
                            colspan=len(self.column_renderers),
                            clazz='details'
                        )
                    ),
                    clazz='regular'
                ) for row in self.j
            ),
            clazz=' '.join(
                f"hide-c-{i + 2}"
                for i, column_renderer in enumerate(self.column_renderers)
                if column_renderer.collapsed
            )
        )
        return str(t)
