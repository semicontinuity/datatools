import datetime
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
        return "<font color='#808000'>null</font>"
    elif v is True:
        return "<font color='#40C040'>true</font>"
    elif v is False:
        return "<font color='#6060C0'>false</font>"
    elif type(v) is int or type(v) is float:
        return f"<font color='#C06060'>{v}</font>"
    elif type(v) is datetime.datetime or type(v) is datetime.date or type(v) is datetime.time:
        return f"<font color='#0080E0'>{v}</font>"
    else:
        return f"<font color='#40A0C0'>{v}</font>"


def render_table_cell(is_pk: bool, key: str, value: Any):
    u1 = '<u>' if is_pk else ''
    u2 = '</u>' if is_pk else ''
    return f'''
<tr>
<td valign='bottom' align='left' port="{key}.l" border="1">{u1}{key}{u2}</td>
<td valign='bottom' align='left' port="{key}.r" border="1">{u1}{render_value(value)}{u2}</td>
</tr>
'''


def render_table_cells(d: DbEntityData, row: dict[str, Any], fks: set[str]):
    return "\n".join(render_table_cell(k in d.pks or k in fks, k, v) for k, v in row.items() if should_render(v))


def render_table_record_as_label(d: DbEntityData, row: dict[str, Any], fks: set[str]):
    return f'''<<table border='0' cellspacing='0' cellpadding='1'>
    <tr><td align='left' colspan='2'><b>{d.query.table}</b></td></tr>
    {render_table_cells(d, row, fks)}
</table>>'''


def make_graph():
    dot = Digraph('DatabaseRecords', format='png')
    dot.attr(rankdir='LR')  # Set layout direction to left-to-right
    return dot


def make_subgraph(db_entity_data, subgraph_id: str, fks: set[str]):
    t = Digraph(name=f'cluster_{subgraph_id}')
    t.attr(style='invis')
    t.node(
        subgraph_id,
        shape='none',
        fontname='Courier New',
        fontsize='10',
        label=render_table_record_as_label(db_entity_data, db_entity_data.rows[0], fks)
    )
    return t
