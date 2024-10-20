import mmh3

from datatools.json.coloring_hash import color_string, hash_to_rgb
from datatools.json.util import escape
from util.html.elements import span


def primitive_node(v):
    if v is None:
        return span('null', clazz='null')
    elif type(v) is str:
        return span('"' + ''.join([escape(c) for c in v]) + '"', clazz='string')
    elif v is True:
        return span('true', clazz='true')
    elif v is False:
        return span('false', clazz='false')
    else:
        return span(v, clazz='number')


def style_for_indent(indent: int):
    return 'background-color: ' + color_string(hash_to_rgb(mmh3.hash(str(indent), 0x10ADF00D), offset=0xD0)) + ';'
