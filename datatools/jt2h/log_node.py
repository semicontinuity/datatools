from typing import Dict, List

from datatools.jt2h.column_renderer import ColumnRenderer
from datatools.jt2h.json_node import JsonNode
from datatools.jt2h.json_node_delegate_yaml2 import JsonNodeDelegateYaml2
from util.html.elements import table, td, tr, thead, tbody, th, span


class LogNode:

    def __init__(self, j: List[Dict], column_renderers: List[ColumnRenderer], dynamic_columns: bool = True, dynamic_rows: bool = True) -> None:
        self.j = j
        self.column_renderers = column_renderers
        self.dynamic_columns = dynamic_columns
        self.dynamic_rows = dynamic_rows

    def __str__(self) -> str:
        t = table(
            thead(
                th() if self.dynamic_columns else None,
                (
                    th(
                        span(column_renderer.column, clazz='regular'),
                        span(column_renderer.column[:1], clazz='compact') if self.dynamic_columns else None,
                        onclick=f'toggleParentClass(this, "TABLE", "hide-c-{i + 2}")' if self.dynamic_columns else None
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
                        ) if self.dynamic_columns else None,
                        (
                            column_renderer.render_cell(row)
                            for column_renderer in self.column_renderers
                        ),
                    ),
                    tr(
                        th(clazz='details') if self.dynamic_columns else None,
                        td(
                            JsonNode(row, JsonNodeDelegateYaml2()),
                            colspan=len(self.column_renderers),
                            clazz='details'
                        )
                    ) if self.dynamic_rows else None,
                    clazz='regular'
                ) for row in self.j
            ),
            clazz=' '.join(
                f"hide-c-{i + 2}"
                for i, column_renderer in enumerate(self.column_renderers)
                if column_renderer.collapsed
            ) if self.dynamic_columns else None
        )
        return str(t)

    def css(self):
        return LogNode.CSS_CORE + LogNode.CSS_DYNAMIC_ELEMENTS + self.css_hide_rules() + self.css_column_renderers()

    def css_column_renderers(self):
        return '\n'.join(
            clazz.CSS
            for clazz in set(type(cr) for cr in self.column_renderers) if hasattr(clazz, 'CSS')
        )

    def css_hide_rules(self):
        return '\n'.join(LogNode.hide_rules(n) for n in range(2, len(self.column_renderers) + 2))

    @staticmethod
    def hide_rules(n):
        return f"""
    table.hide-c-{n}>tbody>tr>td:nth-child({n})>span {{display:none;}}
    table.hide-c-{n}>thead>tr>th:nth-child({n})>span {{display:none;}}
    table.hide-c-{n}>thead>tr>th:nth-child({n})>span.compact {{display:inherit;}}
    table.hide-c-{n}>thead>tr>th:nth-child({n}) {{cursor: zoom-in;}}
    """

    CSS_CORE = '''
thead {border: solid 1px darkgray;}
table {border-collapse: collapse; padding: 0; white-space: nowrap;}
table {background: white;}
th {border-top: solid 1px darkgrey; border-bottom: solid 1px darkgrey; background: #DDD; padding-left: 0.5ex; padding-right: 0.5ex;}
td {border-top: solid 1px #CCC; border-bottom: solid 1px #CCC; padding: 0;}
td {border-left: solid 2px darkgrey;}
td {padding-left: 0.5em; padding-right: 0.5em;}
th {border-left: solid 2px darkgrey;}

td:last-child { width: 100%; }

span { white-space: nowrap;}
    '''

    CSS_DYNAMIC_ELEMENTS = '''
td.details { padding: 0; background: #d0d8dc; font-size: 100%; border: solid 2px darkgray;}
tbody.regular th.details {display: none;}
tbody.regular td.details {display: none;}
tbody.regular span.expanded {display: none;}
tbody.regular span.regular  {cursor: zoom-in;}

tbody.expanded span.regular {display: none;}
tbody.expanded span.expanded {cursor: zoom-out;}
thead th {cursor: zoom-out;}

.compact {display:none;}
'''
