from typing import Any

from datatools.ev.x.pg.db_entity_data import DbEntityData
from graphviz import Digraph


def is_supported_type(v: Any):
    if type(v) is dict or type(v) is list:
        return False
    else:
        return True


def should_render(v: Any):
    return is_supported_type(v) and len(str(v)) < 40


def render_value(v: Any):
    if v is None:
        return 'null'
    elif v is True:
        return 'true'
    elif v is False:
        return 'false'
    else:
        return str(v)


def render_table_cell(key: str, value: Any):
    return f'''
<tr>
<td align='left' port="{key}.l" border="1">{key}</td>
<td align='left' port="{key}.r" border="1">{render_value(value)}</td>
</tr>
'''


def render_table_cells(d: DbEntityData, row: dict[str, Any]):
    return "\n".join(render_table_cell(k, v) for k, v in row.items() if should_render(v))


def render_table_record_as_label(d: DbEntityData, row: dict[str, Any]):
    return f'''<<table border='0' cellspacing='0' cellpadding='1'>
    <tr><td align='left' colspan='2'><b>{d.query.table}</b></td></tr>
    {render_table_cells(d, row)}
</table>>'''


def make_graph():
    dot = Digraph('DatabaseRecords', format='png')
    dot.attr(rankdir='LR')  # Set layout direction to left-to-right
    return dot


def make_subgraph(db_entity_data, query, row):
    t = Digraph(name=f'cluster_{db_entity_data.query.table}')
    t.attr(style='invis')
    t.node(
        query.table,
        shape='none',
        fontname='Courier',
        fontsize='10',
        label=render_table_record_as_label(db_entity_data, row)
    )
    return t
