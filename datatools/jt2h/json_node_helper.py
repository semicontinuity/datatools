import html

import mmh3

from datatools.json.coloring_hash import color_string, hash_to_rgb
from datatools.json.util import escape, basic_escape, simple_escape
from datatools.util.html.elements import span, pre


def primitive_node(v, for_json: bool):
    if v is None:
        return span('null', clazz='null')
    elif type(v) is str:
        if '\n' in v:
            return span(
                [
                    pre(''.join([simple_escape(c) for c in html.escape(line, quote=False)]))
                    for line in v.split('\n')
                ],
                clazz='string'
            )
        else:
            return span(str_repr(v, for_json), clazz='string')
    elif v is True:
        return span('true', clazz='true')
    elif v is False:
        return span('false', clazz='false')
    else:
        return span(v, clazz='number')


def str_repr(v, for_json: bool):
    v = html.escape(v, quote=False)
    if for_json or "'" in v:
        return '"' + ''.join([escape(c) for c in v]) + '"'
    else:
        return "'" + ''.join([basic_escape(c) for c in v]) + "'"


def style_for_indent(indent: int):
    return 'background-color: ' + color_string(hash_to_rgb(mmh3.hash(str(indent), 0x10ADF00D), offset=0xD0)) + ';'
