import datetime
import os
import re
from typing import Any

from graphviz import Digraph

from datatools.ev.x.pg.rrd.model import CardData
from datatools.json.coloring_hash import color_string, hash_code_to_rgb

svg = bool(os.environ.get('SVG'))


def is_valid_uuid(value):
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    return bool(uuid_pattern.match(value))


def is_supported_type(v: Any):
    if type(v) is dict or type(v) is list:
        return False
    elif v is None or type(v) is bool or type(v) is int or type(v) is float:
        return os.environ.get('V')
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


def render_table_cell(key: str, value: Any, is_pk_or_fk: bool, record_pk_value: Any, table: str):
    is_pk_or_fk = is_pk_or_fk or (type(value) is str and is_valid_uuid(value))

    key_u1 = '<u>' if is_pk_or_fk else ''
    key_u2 = '</u>' if is_pk_or_fk else ''

    if value is None:
        val_u1 = ''
        val_u2 = ''
    else:
        val_u1 = key_u1
        val_u2 = key_u2

    # bg = f"bgcolor='{color_string(hash_code_to_rgb(hash(value), dark=not svg))}'" if value is not None and is_pk_or_fk else ''

    # should highlight if there is an edge, starting from this cell.. or no? same colors help to correlate.
    # highlight, if more than 1 occurrence?
    highlight = is_pk_or_fk and value is not None
    highlight_bg = f"bgcolor='{color_string(hash_code_to_rgb(hash(value if highlight else record_pk_value), dark=not svg))}'"
    # key_bg = f"bgcolor='{color_string(hash_code_to_rgb(hash(value if highlight else record_pk_value), dark=not svg))}'"
    key_bg = f"bgcolor='{color_string(hash_code_to_rgb(hash(record_pk_value), dark=not svg))}'"
    val_bg = highlight_bg if highlight else ("bgcolor='#F8F8F8'" if svg else "bgcolor='#101010'")

    return f'''
<tr>
<td valign='bottom' align='left' port='{key}.l' border='1' sides='R' {key_bg}>{key_u1}<b>{key}</b>{key_u2}</td>
<td valign='bottom' align='left' port='{key}.r' border='0'           {val_bg}>{val_u1}<b>{render_value(value)}</b>{val_u2}</td>
</tr>
'''


def render_table_cells(d: CardData, row: dict[str, Any], fks: set[str]):
    record_pk_value = d.rows[0][d.metadata.primaryKeys[0]]
    return "\n".join(
        render_table_cell(k, v, is_pk_or_fk=(k in d.metadata.primaryKeys or k in fks), record_pk_value=record_pk_value, table=d.metadata.table)
        for k, v in row.items()
        if should_render(v)
    )


def render_table_record_as_label1(d: CardData, row: dict[str, Any], fks: set[str]):
    fg = 'black'
    bg = color_string(hash_code_to_rgb(hash(d.metadata.table), dark=not svg, light_offset=0xC0, dark_offset=0x40))

    return f'''<<table cellspacing='0' cellpadding='1,0' border='1' color='gray'>
    <tr><td align='left' colspan='2' border='1' sides='B' bgcolor='{bg}'><b><font color='{fg}'>{d.metadata.table}</font></b></td></tr>
    {render_table_cells(d, row, fks)}
</table>>'''


def make_graph():
    dot = Digraph('DatabaseRecords', format='png')
    rankdir = os.environ.get('RANKDIR') or 'LR'
    dot.attr(rankdir=rankdir)
    return dot


def make_subgraph(db_entity_data, subgraph_id: str, fks: set[str]):
    t = Digraph(name=f'cluster_{subgraph_id}')
    t.attr(style='invis')
    t.node(
        subgraph_id,
        shape='none',
        fontname='Courier New',
        fontsize='10',
        label=render_table_record_as_label1(db_entity_data, db_entity_data.rows[0], fks)
    )
    return t
